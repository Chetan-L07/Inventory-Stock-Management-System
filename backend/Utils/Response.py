def success_response(message, data=None, status_code=200):
    return {
        "status": "Success",
        "message": message,
        "data": data
    }, status_code
    
    
def error_response(message, error_code=None, status_code=400):
    return {
        "status": "Error",
        "message": message,
        "error_code": error_code if error_code else "API error"
    }, status_code