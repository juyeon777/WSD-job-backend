from flask import Blueprint, request, jsonify
from .models import Job
from .. import db
from flask_jwt_extended import jwt_required

jobs_bp = Blueprint('jobs', __name__)

# 채용 공고 조회 API
@jobs_bp.route('/api/jobs', methods=['GET'])
def get_jobs():
    """
    모든 채용 공고 조회 API
    """
    try:
        jobs = Job.query.all()
        return jsonify([job.to_dict() for job in jobs]), 200
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve jobs: {str(e)}"}), 500

# 채용 공고 등록 API
@jobs_bp.route('/api/jobs', methods=['POST'])
@jwt_required()
def add_job():
    """
    새로운 채용 공고 등록 API
    """
    data = request.get_json()

    # 필수 데이터 검증
    if not data.get('title') or not data.get('company_name') or not data.get('url'):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_job = Job(
            job_group=data.get('job_group'),
            badge=data.get('badge'),
            company_name=data['company_name'],
            title=data['title'],
            deadline=data.get('deadline'),
            address_main=data.get('address_main'),
            address_total=data.get('address_total'),
            experience=data.get('experience'),
            education=data.get('education'),
            employment_type=data.get('employment_type'),
            salary=data.get('salary'),
            tech_stack=data.get('tech_stack'),
            crawled_at=data.get('crawled_at'),
            url=data['url'],
            description=data.get('description')
        )
        db.session.add(new_job)
        db.session.commit()
        return jsonify({"message": "Job created successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500

# 채용 공고 삭제 API
@jobs_bp.route('/api/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """
    특정 ID의 채용 공고 삭제 API
    """
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({"message": "Job deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete job: {str(e)}"}), 500

# 채용 공고 크롤링 API
@jobs_bp.route('/api/jobs/crawl', methods=['GET'])
@jwt_required()
def start_crawling():
    """
    사람인 웹사이트에서 채용 공고를 크롤링하여 데이터베이스에 저장
    """
    from .crawler import crawl_saramin, create_table

    create_table()
    crawled_jobs = crawl_saramin(max_jobs=50)
    return jsonify({"message": f"Crawled {len(crawled_jobs)} jobs successfully"}), 200
