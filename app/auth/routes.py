from flask import request, jsonify
from app.models import User
from app import db
from app.auth import auth_bp  # auth_bp를 가져옴
from .utils import generate_token

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already in use"}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user.id)
    return jsonify({"message": "Login successful", "token": token}), 200
