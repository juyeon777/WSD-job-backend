from app.main import create_app, db  # db도 가져와야 함
import logging
import sys

# 로그 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # 로그 파일 기록
        logging.StreamHandler()          # 터미널 출력
    ]
)

# Flask 애플리케이션 생성
app = create_app()

# 테이블 생성 함수
def initialize_database():
    with app.app_context():
        try:
            logging.info("✅ 데이터베이스 테이블 생성 완료!")
        except Exception as e:
            logging.error(f"❌ 데이터베이스 테이블 생성 실패: {e}")
            sys.exit(1)

if __name__ == '__main__':
    try:
        logging.info("Starting the Flask application...")

        # 테이블 생성
        initialize_database()

        # 애플리케이션 실행
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Failed to start the server: {e}")
        sys.exit(1)
