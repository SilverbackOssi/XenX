from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_db
from app.auth.services.google_oauth_service import GoogleOAuthService
from app.auth.services.token_service import TokenService
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

# Get these from your environment variables or settings
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
FRONTEND_BASE_URL = settings.FRONTEND_BASE_URL  # URL to redirect after login

@router.get("/login")
async def google_login():
    """Redirect to Google OAuth login page"""
    oauth_service = GoogleOAuthService(
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        redirect_uri=f"{settings.API_BASE_URL}/auth/google/callback"
    )
    auth_url = oauth_service.get_auth_url()
    print(auth_url)
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def google_callback(
    code: str = Query(...), 
    db: AsyncSession = Depends(get_db)
):
    """Handle the OAuth callback from Google"""
    try:
        oauth_service = GoogleOAuthService(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=f"{settings.API_BASE_URL}/auth/google/callback",
            session=db
        )
        
        # Exchange code for token
        tokens = await oauth_service.exchange_code_for_token(code)
        id_token_jwt = tokens.get("id_token")
        
        # Get user info from ID token
        user_info = await oauth_service.get_user_info(id_token_jwt)
        
        # Authenticate or create user
        user, error = await oauth_service.authenticate_or_create_user(user_info)
        
        if error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error,
                headers={"WWW-Authenticate": "Bearer"}
            )
            
        # Generate tokens
        auth_tokens = TokenService.create_tokens_for_user(user)
        
        # Redirect to frontend with token #XXX
        redirect_url = f"{FRONTEND_BASE_URL}?access_token={auth_tokens['access_token']}&refresh_token={auth_tokens['refresh_token']}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )