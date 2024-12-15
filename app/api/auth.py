from flask import Blueprint, request, current_app
from app.models.models import get_db_connection
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime
from app.api.utils.response import success_response, error_response

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
        return error_response(message="Missing required fields", code="MISSING_FIELDS")

    if not is_valid_email(email):
        return error_response(message="Invalid email format", code="INVALID_EMAIL_FORMAT")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        return error_response(message="Email already exists", code="EMAIL_EXISTS")

    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                   (username, email, hashed_password))
    conn.commit()
    cursor.close()
    conn.close()

    return success_response(data={"message": "User registered successfully"})

# 로그인 (POST /auth/login)
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return error_response(message="Missing required fields", code="MISSING_FIELDS")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    if not user or not check_password_hash(user['password_hash'], password):
        return error_response(message="Invalid email or password", code="INVALID_CREDENTIALS")

    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])

    cursor.execute("INSERT INTO login_history (user_id, login_time) VALUES (%s, %s)",
                   (user['id'], datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

    return success_response(data={
        "access_token": access_token,
        "refresh_token": refresh_token
    })

# 토큰 갱신 (POST /auth/refresh)
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return success_response(data={"access_token": new_access_token})

# 사용자 정보 조회 및 수정 (GET, PUT /auth/profile)
@auth_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT username, email FROM users WHERE id = %s", (current_user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return error_response(message="User not found", code="USER_NOT_FOUND")

        return success_response(data=user)

    elif request.method == 'PUT':
        data = request.get_json()
        new_username = data.get('username')
        new_email = data.get('email')
        new_password = data.get('password')

        if new_email:
            cursor.execute("SELECT id FROM users WHERE email = %s AND id != %s", (new_email, current_user_id))
            if cursor.fetchone():
                return error_response(message="Email already exists", code="EMAIL_EXISTS")

        updates, params = [], []
        if new_username:
            updates.append("username = %s")
            params.append(new_username)
        if new_email:
            updates.append("email = %s")
            params.append(new_email)
        if new_password:
            updates.append("password_hash = %s")
            params.append(generate_password_hash(new_password))

        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            params.append(current_user_id)
            cursor.execute(query, tuple(params))
            conn.commit()

        cursor.close()
        conn.close()
        return success_response(data={"message": "Profile updated successfully"})

# 사용자 삭제 (DELETE /auth/profile)
@auth_bp.route('/profile', methods=['DELETE'])
@jwt_required()
def delete_profile():
    current_user_id = get_jwt_identity()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (current_user_id,))
    conn.commit()
    cursor.close()
    conn.close()

    return success_response(data={"message": "User deleted successfully"})
