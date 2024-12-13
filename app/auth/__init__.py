from flask import Blueprint

# auth 블루프린트 생성
auth_bp = Blueprint('auth', __name__)

# 라우트 불러오기
from app.auth import routes
