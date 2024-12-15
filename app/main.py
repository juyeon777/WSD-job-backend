from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from app.config import Config
from flask_cors import CORS
from app.models.models import get_db_connection

# 확장 초기화
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='../templates')
    
    # 설정 불러오기
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Swagger UI 설정
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, 
        API_URL,
        config={  # Swagger UI 설정
        'app_name': "YeonHire API 문서"
        }
    )
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
        return render_template('index.html')  # 메인 페이지 렌더링
    # 채용 공고 페이지 라우트 추가
    @app.route('/jobs/page')
    def jobs_page():
        try:
            # 데이터베이스 연결
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)  # 결과를 딕셔너리 형태로 반환

            # SQL 쿼리 실행
            query = """
            SELECT title, company_name, job_group, badge, deadline, 
                address_main, address_total, experience, education, 
                employment_type, salary, tech_stack, createdAt, crawledAt, url
            FROM jobs
            ORDER BY createdAt DESC
            """
            cursor.execute(query)
            jobs = cursor.fetchall()  # 모든 데이터 가져오기

            # 연결 종료
            cursor.close()
            conn.close()

            # jobs.html에 데이터 전달
            return render_template('jobs.html', jobs=jobs)

        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return render_template('jobs.html', jobs=[])


    # 블루프린트 테스트 라우트 (옵션)
    @app.route('/ping')
    def ping():
        """
        간단한 서버 상태 확인
        """
        return jsonify({"message": "Server is running", "status": "success"}), 200

    return app
