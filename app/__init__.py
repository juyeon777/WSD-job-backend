from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # SQLAlchemy와 Migrate 초기화
    db.init_app(app)
    migrate.init_app(app, db)

    # 블루프린트 등록
    from app.routers import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
