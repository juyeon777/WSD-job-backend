from flask import Blueprint
from app.api.auth import auth_bp
from app.api.applications import applications_bp
from app.api.jobs import jobs_bp
from app.api.bookmarks import bookmarks_bp

# 메인 API Blueprint
api_bp = Blueprint('api', __name__)

# 하위 블루프린트 등록
api_bp.register_blueprint(auth_bp, url_prefix='/api/auth')
api_bp.register_blueprint(applications_bp, url_prefix='/api/applications')
api_bp.register_blueprint(jobs_bp, url_prefix='/api/jobs')
api_bp.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')
