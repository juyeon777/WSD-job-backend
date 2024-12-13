from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta
import re

def generate_jwt(user_id):
    """
    주어진 사용자 ID로 JWT 토큰 생성
    """
    access_token = create_access_token(identity=user_id, expires_delta=timedelta(days=1))
    return access_token

def validate_email(email):
    """
    이메일 형식 검증
    """
    email_regex = r'^\S+@\S+\.\S+$'
    return re.match(email_regex, email) is not None

def validate_password(password):
    """
    비밀번호 강도 검증 (최소 8자, 대소문자 및 숫자 포함)
    """
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    return True
