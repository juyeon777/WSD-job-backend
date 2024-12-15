from flask import Blueprint, request, jsonify
from app.models.models import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

applications_bp = Blueprint('applications', __name__)

# 지원하기 (POST /applications)
@applications_bp.route('/applications', methods=['POST'])
@jwt_required()
def create_application():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()  # 현재 인증된 사용자 ID
        job_id = data.get('job_id')
        resume_url = data.get('resume_url')  # 선택적으로 이력서 첨부

        if not job_id:
            return jsonify({"error": "Job ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 중복 지원 확인
        cursor.execute("SELECT id FROM applications WHERE user_id = %s AND job_id = %s", (user_id, job_id))
        if cursor.fetchone():
            return jsonify({"error": "You have already applied for this job"}), 400

        # 지원 정보 저장
        cursor.execute("""
            INSERT INTO applications (user_id, job_id, resume_url, status, applied_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, job_id, resume_url, 'applied', datetime.now()))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Application submitted successfully"}), 201

    except Exception as e:
        logging.error(f"Error creating application: {str(e)}")
        return jsonify({"error": "Failed to submit application"}), 500


# 지원 내역 조회 (GET /applications)
@applications_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    try:
        user_id = get_jwt_identity()  # 현재 사용자 ID
        status = request.args.get('status')  # 상태별 필터링 (예: 'applied', 'canceled')
        sort_order = request.args.get('order', 'desc').lower()  # 날짜 정렬 순서 (asc/desc)

        if sort_order not in ['asc', 'desc']:
            sort_order = 'desc'

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # SQL 쿼리 구성
        query = "SELECT * FROM applications WHERE user_id = %s"
        params = [user_id]

        if status:
            query += " AND status = %s"
            params.append(status)

        query += f" ORDER BY applied_at {sort_order}"

        cursor.execute(query, tuple(params))
        applications = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"applications": applications}), 200

    except Exception as e:
        logging.error(f"Error fetching applications: {str(e)}")
        return jsonify({"error": "Failed to fetch applications"}), 500


# 지원 취소 (DELETE /applications/<int:application_id>)
@applications_bp.route('/applications/<int:application_id>', methods=['DELETE'])
@jwt_required()
def cancel_application(application_id):
    try:
        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 지원 상태 확인
        cursor.execute("SELECT status FROM applications WHERE id = %s AND user_id = %s", (application_id, user_id))
        application = cursor.fetchone()

        if not application:
            return jsonify({"error": "Application not found"}), 404

        if application['status'] != 'applied':
            return jsonify({"error": "Cannot cancel this application"}), 400

        # 상태를 'canceled'로 업데이트
        cursor.execute("UPDATE applications SET status = %s, canceled_at = %s WHERE id = %s",
                       ('canceled', datetime.now(), application_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Application canceled successfully"}), 200

    except Exception as e:
        logging.error(f"Error canceling application: {str(e)}")
        return jsonify({"error": "Failed to cancel application"}), 500
