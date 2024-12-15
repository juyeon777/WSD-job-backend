from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from app.config import Config
from app.api import api_bp  # API Blueprint 가져오기
from dotenv import load_dotenv
import os

# 확장 초기화
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

# 환경 변수 로드
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT 설정
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    jwt = JWTManager(app)

    # SQLAlchemy와 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # API Blueprint 등록
    app.register_blueprint(api_bp, url_prefix='/api')

    # 홈 라우트 (테스트용)
    @app.route('/')
    def index():
        return {"message": "Welcome to the Job Management API!"}, 200

    return app
