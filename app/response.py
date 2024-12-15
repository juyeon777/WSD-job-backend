from flask import jsonify

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
