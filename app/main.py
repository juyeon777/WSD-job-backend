from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from app.config import Config

# 확장 초기화
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # 설정 불러오기
    app.config.from_object(Config)

    # 확장 초기화
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Swagger UI 설정
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # 블루프린트 등록
    from app.api.auth import auth_bp
    from app.api.jobs import jobs_bp
    from app.api.applications import applications_bp
    from app.api.bookmarks import bookmarks_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(jobs_bp, url_prefix='/jobs')
    app.register_blueprint(applications_bp, url_prefix='/applications')
    app.register_blueprint(bookmarks_bp, url_prefix='/bookmarks')

    # 기본 라우트
    @app.route('/')
    def index():
        return "<h1>Welcome to the Job Listings Application</h1><p>Explore the API routes.</p>"

    return app
