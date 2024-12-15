from flask import Flask
from flask_jwt_extended import JWTManager
from app.api import api_bp
from app.api.models.models import get_db_connection  # 데이터베이스 연결 확인용
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    # JWT 설정
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    jwt = JWTManager(app)

    # API Blueprint 등록
    app.register_blueprint(api_bp, url_prefix='/api')

    # 홈 라우트 (테스트용)
    @app.route('/')
    def index():
        return {"message": "Welcome to the Job Management API!"}, 200

    return app
