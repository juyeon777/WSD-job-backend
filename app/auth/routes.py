from flask import Blueprint, request, jsonify
from app.models import User
from app import db, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Blueprint 생성
auth_bp = Blueprint('auth', __name__)

# 회원 가입 API
@auth_bp.route('/register', methods=['POST'])
def signup():
    data = request.get_json()

    # 필수 데이터 검증
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    # 중복된 사용자 이름 검증
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "Username already exists"}), 400

    # 비밀번호 해싱 및 사용자 생성
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)

    # 데이터베이스에 저장
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201

# 로그인 API
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    # 필수 데이터 검증
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    # 사용자 조회 및 비밀번호 검증
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token}), 200

    return jsonify({"error": "Invalid username or password"}), 401

# 사용자 정보 조회 API
@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if user:
        return jsonify(user.to_dict()), 200

    return jsonify({"error": "User not found"}), 404

# 사용자 정보 수정 API
@auth_bp.route('/user', methods=['PUT'])
@jwt_required()
def update_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    # 수정 가능한 필드 업데이트
    if 'username' in data:
        # 중복된 사용자 이름 확인
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
        user.username = data['username']

    if 'email' in data:
        # 중복된 이메일 확인
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
        user.email = data['email']

    if 'password' in data:
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user.password = hashed_password

    db.session.commit()
    return jsonify({"message": "User updated successfully"}), 200

# 사용자 탈퇴 API
@auth_bp.route('/user', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"}), 200
