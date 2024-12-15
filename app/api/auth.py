from flask import Blueprint, request, current_app, jsonify
from app.models.models import get_db_connection
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import re
from datetime import datetime
import logging

auth_bp = Blueprint('auth', __name__)

# 성공 응답 함수
def success_response(data=None, pagination=None):
    """
    성공 응답을 생성하는 함수
    :param data: 실제 반환할 데이터 (dict, list 등)
    :param pagination: 페이지네이션 정보 (dict)
    :return: JSON 형식의 성공 응답
    """
    response = {
        "status": "success",
        "data": data if data else {}
    }
    if pagination:
        response["pagination"] = pagination
    return jsonify(response), 200

# 실패 응답 함수
def error_response(message="An error occurred", code="ERROR"):
    """
    실패 응답을 생성하는 함수
    :param message: 에러 메시지
    :param code: 에러 코드
    :return: JSON 형식의 실패 응답
    """
    response = {
        "status": "error",
        "message": message,
        "code": code
    }
    return jsonify(response), 400

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


# 로그아웃 (POST /auth/logout)
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]  # JWT의 고유 ID
        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 블랙리스트에 토큰 저장
        cursor.execute("""
            INSERT INTO token_blacklist (jti, user_id, revoked_at)
            VALUES (%s, %s, %s)
        """, (jti, user_id, datetime.now()))
        conn.commit()

        cursor.close()
        conn.close()

        return success_response(data={"message": "Successfully logged out"})
    except Exception as e:
        logging.error(f"Error logging out: {str(e)}")
        return error_response(message="Failed to log out", code="LOGOUT_FAILED")
    
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

# 사용자 활동 로그 조회 (GET /auth/activity)
@auth_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_user_activity():
    try:
        user_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 로그인 이력 조회
        cursor.execute("""
            SELECT login_time FROM login_history WHERE user_id = %s ORDER BY login_time DESC
        """, (user_id,))
        login_history = cursor.fetchall()

        # 지원 이력 조회
        cursor.execute("""
            SELECT job_id, applied_at, status FROM applications WHERE user_id = %s ORDER BY applied_at DESC
        """, (user_id,))
        applications = cursor.fetchall()

        # 북마크 이력 조회
        cursor.execute("""
            SELECT job_id, bookmarked_at FROM bookmarks WHERE user_id = %s ORDER BY bookmarked_at DESC
        """, (user_id,))
        bookmarks = cursor.fetchall()

        cursor.close()
        conn.close()

        return success_response(data={
            "login_history": login_history,
            "applications": applications,
            "bookmarks": bookmarks
        })
    except Exception as e:
        logging.error(f"Error fetching activity log: {str(e)}")
        return error_response(message="Failed to fetch activity log", code="ACTIVITY_LOG_FAILED")
