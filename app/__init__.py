from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_bcrypt import Bcrypt

# 확장 초기화
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # SQLAlchemy와 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트 등록
    from app.auth.routes import auth_bp  # 회원 관리 블루프린트
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.jobs.routes import jobs_bp  # 채용 공고 관련 블루프린트
    app.register_blueprint(jobs_bp, url_prefix='/jobs')

    return app
