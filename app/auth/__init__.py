from flask import Blueprint

# auth_bp 블루프린트 정의
auth_bp = Blueprint('auth', __name__)

from . import routes  # routes.py 가져오기
