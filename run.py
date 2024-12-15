from flask import Flask, render_template, jsonify
from app.auth.routes import auth_bp  # /auth 블루프린트 가져오기
from app import db, bcrypt  # SQLAlchemy 및 Bcrypt 가져오기
from flask_jwt_extended import JWTManager
import mysql.connector
import logging
import os
import sys
from flask_swagger_ui import get_swaggerui_blueprint

def create_app():
    app = Flask(__name__)

    # Flask 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:juyeon777@localhost/job_portal'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'

    # MySQL 연결 정보
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'juyeon777',
        'database': 'job_portal',
        'charset': 'utf8mb4'
    }

    # 확장 초기화
    db.init_app(app)
    bcrypt.init_app(app)
    JWTManager(app)

    # Swagger UI 설정
    SWAGGER_URL = '/swagger'
    API_URL = '/static/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    # 경로 설정
    @app.route('/jobs')
    def jobs():
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)

            query = """
            SELECT job_group, badge, company_name, title, deadline, 
                   address_main, address_total, experience, education, 
                   employment_type, salary, tech_stack, createdAt, 
                   crawledAt, url, description
            FROM jobs
            """
            cursor.execute(query)
            jobs_data = cursor.fetchall()

            cursor.close()
            conn.close()

            app.logger.info(f"Retrieved {len(jobs_data)} job listings")
            return render_template('jobs.html', jobs=jobs_data)
        except mysql.connector.Error as e:
            app.logger.error(f"Database error: {e}")
            return jsonify({"error": "Database error", "details": str(e)}), 500
        except Exception as e:
            app.logger.error(f"Unexpected error in /jobs route: {e}")
            return jsonify({"error": "Unexpected error", "details": str(e)}), 500

    @app.route('/')
    def index():
        return "<h1>Welcome to the Job Listings Application</h1><p>Go to <a href='/jobs'>/jobs</a> to see job listings.</p>"

    # auth 블루프린트 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

if __name__ == '__main__':
    try:
        # Flask 애플리케이션 생성
        app = create_app()

        # 로그 설정
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s]: %(message)s',
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )

        # Flask 실행
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000
        )
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)
