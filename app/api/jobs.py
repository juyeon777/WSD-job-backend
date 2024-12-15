from flask import Blueprint, request, jsonify
from app.models.models import get_db_connection
import logging

jobs_bp = Blueprint('jobs', __name__)

# 유효한 정렬 필드 목록
VALID_SORT_FIELDS = {'createdAt', 'title', 'company_name', 'salary'}

# 채용 공고 목록 조회 (GET /jobs)
@jobs_bp.route('/jobs', methods=['GET'])
def get_jobs():
    try:
        # 요청 파라미터
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 20))
        sort = request.args.get('sort', 'createdAt')  # 정렬 기준
        order = request.args.get('order', 'desc').lower()  # 정렬 순서
        region = request.args.get('region')  # 지역 필터
        career = request.args.get('career')  # 경력 필터
        salary = request.args.get('salary')  # 급여 필터
        tech_stack = request.args.get('tech_stack')  # 기술 스택 필터
        keyword = request.args.get('keyword')  # 검색 키워드

        # 정렬 필드 검증
        if sort not in VALID_SORT_FIELDS:
            sort = 'createdAt'
        if order not in ['asc', 'desc']:
            order = 'desc'

        # SQL 쿼리 구성
        query = "SELECT * FROM jobs"
        count_query = "SELECT COUNT(*) as total FROM jobs"
        filters = []
        params = []

        if region:
            filters.append("address_main = %s")
            params.append(region)
        if career:
            filters.append("experience = %s")
            params.append(career)
        if salary:
            filters.append("salary = %s")
            params.append(salary)
        if tech_stack:
            filters.append("tech_stack LIKE %s")
            params.append(f"%{tech_stack}%")
        if keyword:
            filters.append("(title LIKE %s OR company_name LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        if filters:
            filter_clause = " WHERE " + " AND ".join(filters)
            query += filter_clause
            count_query += filter_clause

        query += f" ORDER BY {sort} {order} LIMIT %s OFFSET %s"
        params.extend([size, (page - 1) * size])

        # 데이터베이스 연결 및 쿼리 실행
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 데이터 조회
        cursor.execute(query, tuple(params))
        jobs = cursor.fetchall()

        # 총 개수 조회
        cursor.execute(count_query, tuple(params[:len(filters)]))  # 필터에 맞는 총 개수만 계산
        total_count = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        return jsonify({
            "data": jobs,
            "pagination": {
                "currentPage": page,
                "pageSize": size,
                "totalItems": total_count
            }
        }), 200

    except Exception as e:
        logging.error(f"Error fetching jobs: {str(e)}")
        return jsonify({"error": "Failed to fetch jobs"}), 500


# 채용 공고 상세 조회 (GET /jobs/<id>)
@jobs_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 상세 정보 조회
        cursor.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # 조회수 컬럼이 존재하는지 확인 후 증가
        try:
            cursor.execute("UPDATE jobs SET views = views + 1 WHERE id = %s", (job_id,))
            conn.commit()
        except:
            logging.warning("No 'views' column found. Skipping view count update.")

        # 관련 공고 추천 (같은 기술 스택 기준)
        if job['tech_stack']:
            cursor.execute("""
                SELECT id, title, company_name, address_main 
                FROM jobs 
                WHERE tech_stack LIKE %s AND id != %s 
                LIMIT 5
            """, (f"%{job['tech_stack']}%", job_id))
            related_jobs = cursor.fetchall()
        else:
            related_jobs = []

        cursor.close()
        conn.close()

        return jsonify({
            "job": job,
            "related_jobs": related_jobs
        }), 200

    except Exception as e:
        logging.error(f"Error fetching job details: {str(e)}")
        return jsonify({"error": "Failed to fetch job details"}), 500