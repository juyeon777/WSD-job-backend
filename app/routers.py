from flask import Blueprint, jsonify
from app.models import Job

bp = Blueprint('routes', __name__)

@bp.route('/')
def home():
    return "MySQL 연결 완료!"

@bp.route('/jobs', methods=['GET'])
def get_jobs():
    

    jobs = Job.query.all()
    job_list = [{
        'id': job.id,
        'title': job.title,
        'company_name': job.company_name,
        'location': job.location,
        'deadline': job.deadline.strftime('%Y-%m-%d'),
        'description': job.description
    } for job in jobs]
    return jsonify(job_list)
