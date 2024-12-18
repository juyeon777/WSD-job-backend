from flask import Blueprint, request, jsonify
from app.models.models import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

bookmarks_bp = Blueprint('bookmarks', __name__)

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

@bookmarks_bp.route('/')
@jwt_required()
def bookmarks_root():
    return success_response(data={"message": "Bookmarks API root"})

# 북마크 추가/제거 (POST /bookmarks)
@bookmarks_bp.route('', methods=['POST'])
@jwt_required()
def toggle_bookmark():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        job_id = data.get('job_id')

        if not job_id:
            return {"status": "error", "message": "Job ID is required"}, 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 북마크 확인
        cursor.execute("SELECT id FROM bookmarks WHERE user_id = %s AND job_id = %s", (user_id, job_id))
        existing = cursor.fetchone()

        if existing:
            # 북마크 제거
            cursor.execute("DELETE FROM bookmarks WHERE id = %s", (existing['id'],))
            message = "Bookmark removed successfully"
        else:
            # 북마크 추가
            cursor.execute("INSERT INTO bookmarks (user_id, job_id) VALUES (%s, %s)", (user_id, job_id))
            message = "Bookmark added successfully"

        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success", "message": message}, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


# 북마크 목록 조회 (GET /bookmarks)
@bookmarks_bp.route('', methods=['GET'])
@jwt_required()
def get_bookmarks():
    try:
        user_id = get_jwt_identity()  # 현재 인증된 사용자 ID
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        offset = (page - 1) * size

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 북마크 목록 조회 (최신순 정렬)
        cursor.execute("""
            SELECT b.id AS bookmark_id, b.bookmarked_at, 
                   j.id AS job_id, j.title, j.company_name, j.address_main
            FROM bookmarks b
            JOIN jobs j ON b.job_id = j.id
            WHERE b.user_id = %s
            ORDER BY b.bookmarked_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, size, offset))
        bookmarks = cursor.fetchall()

        # 총 북마크 개수 조회
        cursor.execute("""
            SELECT COUNT(*) AS total FROM bookmarks WHERE user_id = %s
        """, (user_id,))
        total_count = cursor.fetchone()['total']

        cursor.close()
        conn.close()

        pagination = {
            "currentPage": page,
            "pageSize": size,
            "totalItems": total_count
        }

        return success_response(data=bookmarks, pagination=pagination)

    except Exception as e:
        logging.error(f"Error fetching bookmarks: {str(e)}")
        return error_response(message="Failed to fetch bookmarks", code="BOOKMARK_FETCH_FAILED")
