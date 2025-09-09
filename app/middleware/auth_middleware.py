from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.auth.services import token_service
from app.auth.database import AsyncSessionLocal
from app.auth.models.users import User

async def auth_gateway_middleware(request: Request, call_next):
    """
    Middleware to authenticate requests, attach user data to request state,
    and prepare for routing to microservices.
    """
    # Paths that do not require authentication
    public_paths = [
        "/api/v1/docs", 
        "/api/v1/redoc", 
        "/api/v1/openapi.json",
        "/api/v1/health", 
        "/api/v1/auth/login", 
        "/api/v1/auth/register",
        "/api/v1/auth/verify-email",
        "/api/v1/recovery/forgot-password",
        "/api/v1/recovery/reset-password",
    ]
    
    # Allow OPTIONS requests for CORS preflight
    if request.method == "OPTIONS":
        return await call_next(request)

    # Check if the request path is public
    if any(request.url.path.startswith(path) for path in public_paths):
        response = await call_next(request)
        return response

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication required"},
        )

    token = auth_header.split("Bearer ")[1]
    
    try:
        payload = token_service.verify_and_decode_token(token, expected_type="access")
        user_id = payload.get("id")
        token_ver = payload.get("ver")

        if user_id is None or token_ver is None:
            raise ValueError("User ID not in token payload")
            
        # Attach user info to the request state for downstream use
        async with AsyncSessionLocal() as db:
            # Use the session directly to get the user by ID
            user = await db.get(User, user_id)

            if not user or not user.is_active or user.token_version != token_ver:
                 return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found or Token is invalidated/Revoked"},
                )
            request.state.user = user
    
    except token_service.jwt.InvalidTokenError as e:
        return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(e)},
    )
    except Exception as e:
        return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": f"Invalid token: {str(e)}"},
    )

    response = await call_next(request)
    return response