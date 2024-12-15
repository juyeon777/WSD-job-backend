from flask import Blueprint, request, jsonify, current_app
from app.models.models import get_db_connection
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# 이메일 검증 함수
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email)

# 회원 가입 (POST /auth/register)
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password or not username:
        return jsonify({"error": "Missing required fields"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 중복 회원 검사
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = generate_password_hash(password)

    # 사용자 정보 저장
    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                   (username, email, hashed_password))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "User registered successfully"}), 201

# 로그인 (POST /auth/login)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 사용자 인증
    cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Invalid email or password"}), 401

    # 토큰 발급
    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])

    # 로그인 이력 저장
    cursor.execute("INSERT INTO login_history (user_id, login_time) VALUES (%s, %s)",
                   (user['id'], datetime.now()))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# 토큰 갱신 (POST /auth/refresh)
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({"access_token": new_access_token}), 200

# 사용자 정보 조회 및 수정 (GET, PUT /auth/profile)
@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        # 사용자 정보 조회
        cursor.execute("SELECT username, email FROM users WHERE id = %s", (current_user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(user), 200

    elif request.method == 'PUT':
        # 사용자 정보 수정
        data = request.get_json()
        new_username = data.get('username')
        new_email = data.get('email')
        new_password = data.get('password')

        # 중복 검사
        if new_email:
            cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, current_user_id))
            if cursor.fetchone():
                return jsonify({"error": "Email already exists"}), 400

        updates = []
        params = []

        if new_username:
            updates.append("username = %s")
            params.append(new_username)
        if new_email:
            updates.append("email = %s")
            params.append(new_email)
        if new_password:
            hashed_password = generate_password_hash(new_password)
            updates.append("password_hash = %s")
            params.append(hashed_password)

        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            params.append(current_user_id)
            cursor.execute(query, tuple(params))
            conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Profile updated successfully"}), 200

# 사용자 삭제 (DELETE /auth/profile)
@auth_bp.route('/profile', methods=['DELETE'])
@jwt_required()
def delete_profile():
    current_user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 사용자 삭제
    cursor.execute("DELETE FROM users WHERE id = %s", (current_user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "User deleted successfully"}), 200
