from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from app.config import Config
from flask_cors import CORS

# 확장 초기화
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # 설정 불러오기
    app.config.from_object(Config)
    CORS(app)
    # 확장 초기화
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Swagger UI 설정
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    from app.api.auth import auth_bp
    from app.api.jobs import jobs_bp
    from app.api.applications import applications_bp
    from app.api.bookmarks import bookmarks_bp

    # 블루프린트에 CORS 적용
    CORS(auth_bp)
    CORS(jobs_bp)
    CORS(applications_bp)
    CORS(bookmarks_bp)

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')

    # 기본 라우트
    @app.route('/')
    def index():
        """
        홈 라우트 - API 설명
        """
        return """
        <h1>Welcome to the Job Listings Application</h1>
        <p>Explore the available API routes below:</p>
        <ul>
            <li><strong>Swagger Documentation:</strong> <a href="/swagger" target="_blank">/swagger</a></li>
            <li><strong>Auth API:</strong> <a href="/api/auth" target="_blank">/auth</a></li>
            <li><strong>Jobs API:</strong> <a href="/api/jobs" target="_blank">/jobs</a></li>
            <li><strong>Applications API:</strong> <a href="/api/applications" target="_blank">/applications</a></li>
            <li><strong>Bookmarks API:</strong> <a href="/api/bookmarks" target="_blank">/bookmarks</a></li>
        </ul>
        <p>Use the Swagger UI for testing and exploring the API endpoints.</p>
        """

    # 블루프린트 테스트 라우트 (옵션)
    @app.route('/ping')
    def ping():
        """
        간단한 서버 상태 확인
        """
        return jsonify({"message": "Server is running", "status": "success"}), 200

    return app
