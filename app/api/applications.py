from flask import Blueprint, request, jsonify
from app.models.models import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

applications_bp = Blueprint('applications', __name__)

# 성공 응답 함수
def success_response(data=None, pagination=None):
    """
    성공 응답을 생성하는 함수
    :param data: 실제 반환할 데이터 (dict, list 등)
    :param pagination: 페이지네이션 정보 (dict)
    :return: JSON 형식의 성공 응답
    """
    response = {
        "status": "success",
        "data": data if data else {}
    }
    if pagination:
        response["pagination"] = pagination
    return jsonify(response), 200

# 실패 응답 함수
def error_response(message="An error occurred", code="ERROR"):
    """
    실패 응답을 생성하는 함수
    :param message: 에러 메시지
    :param code: 에러 코드
    :return: JSON 형식의 실패 응답
    """
    response = {
        "status": "error",
        "message": message,
        "code": code
    }
    return jsonify(response), 400

@applications_bp.route('/')
@jwt_required()
def applications_root():
    return success_response(data={"message": "Applications API root"})

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
            return error_response(message="Job ID is required", code="JOB_ID_REQUIRED")

        conn = get_db_connection()
        cursor = conn.cursor()

        # 중복 지원 확인
        cursor.execute("SELECT id FROM applications WHERE user_id = %s AND job_id = %s", (user_id, job_id))
        if cursor.fetchone():
            return error_response(message="You have already applied for this job", code="DUPLICATE_APPLICATION")

        # 지원 정보 저장
        cursor.execute("""
            INSERT INTO applications (user_id, job_id, resume_url, status, applied_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, job_id, resume_url, 'applied', datetime.now()))
        conn.commit()

        cursor.close()
        conn.close()

        return success_response(data={"message": "Application submitted successfully"})

    except Exception as e:
        logging.error(f"Error creating application: {str(e)}")
        return error_response(message="Failed to submit application", code="APPLICATION_SUBMISSION_FAILED")


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

        return success_response(data={"applications": applications})

    except Exception as e:
        logging.error(f"Error fetching applications: {str(e)}")
        return error_response(message="Failed to fetch applications", code="FETCH_APPLICATIONS_FAILED")


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
            return error_response(message="Application not found", code="APPLICATION_NOT_FOUND")

        if application['status'] != 'applied':
            return error_response(message="Cannot cancel this application", code="INVALID_APPLICATION_STATUS")

        # 상태를 'canceled'로 업데이트
        cursor.execute("UPDATE applications SET status = %s, canceled_at = %s WHERE id = %s",
                       ('canceled', datetime.now(), application_id))
        conn.commit()

        cursor.close()
        conn.close()

        return success_response(data={"message": "Application canceled successfully"})

    except Exception as e:
        logging.error(f"Error canceling application: {str(e)}")
        return error_response(message="Failed to cancel application", code="APPLICATION_CANCELLATION_FAILED")
