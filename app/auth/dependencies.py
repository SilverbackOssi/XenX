from fastapi import Depends, HTTPException, status, Request
from typing import List
from app.auth.models.users import User

def get_current_user(request: Request) -> User:
    """
    Retrieves the user object that was attached to the request state
    by the auth_gateway_middleware.
    """
    user = getattr(request.state, "user", None)
    if user is None:
        # This should not happen if the middleware is configured correctly
        # on the route, but it's a good safeguard.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user

class RoleChecker:
    """
    A dependency class that checks if the current user has one of the
    required roles.
    
    Usage:
    @app.get("/admin", dependencies=[Depends(RoleChecker(["admin"]))])
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User with role '{current_user.role}' is not permitted to access this resource.",
            )