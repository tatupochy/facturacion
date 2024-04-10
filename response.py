def create_response(status, code, message, data=None, error=None):
    response_data = {
        'status': status,
        'code': code,
        'message': message,
        'data': data,
        'error': error
    }
    return response_data