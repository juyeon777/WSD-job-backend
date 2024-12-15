from app.main import create_app
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

if __name__ == '__main__':
    try:
        logging.info("Starting the Flask application...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Failed to start the server: {e}")
        sys.exit(1)
