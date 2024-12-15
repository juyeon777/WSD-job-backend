from flask import Blueprint, request, jsonify
from app.models.models import get_db_connection
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from datetime import datetime

bookmarks_bp = Blueprint('bookmarks', __name__)

# 북마크 추가/제거 (POST /bookmarks)
@bookmarks_bp.route('/bookmarks', methods=['POST'])
@jwt_required()
def toggle_bookmark():
    try:
        user_id = get_jwt_identity()  # 현재 인증된 사용자 ID
        data = request.get_json()
        job_id = data.get('job_id')

        if not job_id:
            return jsonify({"error": "Job ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 북마크 존재 여부 확인
        cursor.execute("""
            SELECT id FROM bookmarks WHERE user_id = %s AND job_id = %s
        """, (user_id, job_id))
        bookmark = cursor.fetchone()

        if bookmark:
            # 북마크 제거
            cursor.execute("""
                DELETE FROM bookmarks WHERE user_id = %s AND job_id = %s
            """, (user_id, job_id))
            message = "Bookmark removed successfully"
        else:
            # 북마크 추가
            cursor.execute("""
                INSERT INTO bookmarks (user_id, job_id, bookmarked_at)
                VALUES (%s, %s, %s)
            """, (user_id, job_id, datetime.now()))
            message = "Bookmark added successfully"

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": message}), 200

    except Exception as e:
        logging.error(f"Error toggling bookmark: {str(e)}")
        return jsonify({"error": "Failed to toggle bookmark"}), 500


# 북마크 목록 조회 (GET /bookmarks)
@bookmarks_bp.route('/bookmarks', methods=['GET'])
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

        return jsonify({
            "data": bookmarks,
            "pagination": {
                "currentPage": page,
                "pageSize": size,
                "totalItems": total_count
            }
        }), 200

    except Exception as e:
        logging.error(f"Error fetching bookmarks: {str(e)}")
        return jsonify({"error": "Failed to fetch bookmarks"}), 500
