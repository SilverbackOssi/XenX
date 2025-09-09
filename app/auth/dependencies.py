from fastapi import Depends, HTTPException, status, Request
from typing import List
from app.auth.models.users import User
from fastapi.security import OAuth2PasswordBearer
from app.config import get_settings
from app.auth.services import token_service
from app.auth.database import AsyncSessionLocal

settings = get_settings()


# def get_current_user(request: Request) -> User:
#     """
#     Retrieves the user object that was attached to the request state
#     by the auth_gateway_middleware.
#     """
#     user = getattr(request.state, "user", None)
#     if user is None:
#         # This should not happen if the middleware is configured correctly
#         # on the route, but it's a good safeguard.
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Not authenticated",
#         )
#     return user


# Only enable OAuth2 scheme in dev for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") if settings.ENVIRONMENT == "dev" else None

async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme) if oauth2_scheme else None,
) -> User:
    """
    Returns the authenticated user.  
    - In prod: relies on middleware attaching `request.state.user`.  
    - In dev/Swagger: falls back to decoding the token directly.
    """
    # Case 1: Normal flow (middleware already set the user)
    user = getattr(request.state, "user", None)
    if user:
        return user

    # Case 2: Docs/Swagger fallback (decode manually)
    if token:
        try:
            payload = token_service.verify_and_decode_token(token, expected_type="access")
            user_id = payload.get("id")
            token_ver = payload.get("ver")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no user id",
                )

            # Fetch the user from DB
            async with AsyncSessionLocal() as db:
                user = await db.get(User, user_id)

                if not user or not user.is_active or user.token_version != token_ver:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found or token invalidated",
                    )

                return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )

    # Case 3: Neither middleware nor token worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )


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