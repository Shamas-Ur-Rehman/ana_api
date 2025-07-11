from fastapi.responses import JSONResponse

def success_response(data: dict = None, message: str = "Success", code: int = 200):
    return JSONResponse(
        status_code=code,
        content={
            "message": message,
            "code": code,
            "data": data or {}
        }
    )

def error_response(message: str = "Something went wrong", code: int = 500):
    return JSONResponse(
        status_code=code,
        content={
            "message": message,
            "code": code,
            "data": None
        }
    )
