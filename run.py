from flask import Flask, render_template
import mysql.connector
import logging
import os
import sys

# 애플리케이션 생성
app = Flask(__name__)

# MySQL 데이터베이스 연결 정보
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'juyeon777',
    'database':'job_portal',
    'charset': 'utf8mb4'
}

# /jobs 경로 처리
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
        return f"A database error occurred: {e}", 500
    except Exception as e:
        app.logger.error(f"Unexpected error in /jobs route: {e}")
        return f"An unexpected error occurred: {e}", 500

# 기본 경로 처리
@app.route('/')
def index():
    return "<h1>Welcome to the Job Listings Application</h1><p>Go to <a href='/jobs'>/jobs</a> to see job listings.</p>"

if __name__ == '__main__':
    try:
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
            debug=os.getenv('FLASK_DEBUG', 'False') == 'True',
            host='0.0.0.0',
            port=int(os.getenv('PORT', 5000))
        )
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)
