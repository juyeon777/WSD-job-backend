from app import create_app
import logging
import os
import sys

# 애플리케이션 생성
app = create_app()

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
