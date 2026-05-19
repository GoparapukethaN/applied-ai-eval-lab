from fastapi import HTTPException, status


def bad_request(message: str, code: str = "bad_request") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"code": code, "message": message},
    )


def not_found(message: str, code: str = "not_found") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"code": code, "message": message},
    )

