import jwt
from datetime import datetime, timedelta
from flask import current_app

def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)  # 24시간 유효
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
