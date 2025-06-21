from functools import wraps
from fastapi import HTTPException

def router_try_wrapper(func):
    """
    A decorator to handle exceptions in FastAPI routers.
    It catches all exceptions, logs them, and raises an HTTPException with a 500 status code.
    If the exception is an HTTPException, it is raised without modification.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException as httpe:
            print("Error:", httpe)
            raise
        except Exception as e:
            print("Unexpected error in router:", e)
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper