from fastapi import HTTPException, status

def require_roles(user, allowed_roles: list[str]):
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail = "You do not have permission to perform this action"
        )
    return True