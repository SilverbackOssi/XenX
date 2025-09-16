from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_db
from app.auth.services.google_oauth_service import GoogleOAuthService
from app.auth.services.token_service import TokenService
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth/google", tags=["Google OAuth"])

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
FRONTEND_BASE_URL = settings.FRONTEND_BASE_URL  # URL to redirect after login

@router.get("/login")
async def google_login(request: Request):
    """Get Google OAuth login URL"""
    # For development purposes, detect if we're running locally
    host = request.headers.get("host", "")
    is_local = host.startswith("localhost") or host.startswith("127.0.0.1")
    
    # Use the correct redirect URI based on environment
    if is_local:
        redirect_uri = f"http://{host}/api/v1/auth/google/callback"
        print(f"Using local redirect URI: {redirect_uri}")
    else:
        redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    print(f"Using redirect URI: {redirect_uri}")
    
    # Check if Google OAuth is configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured"
        )
    
    try:
        oauth_service = GoogleOAuthService(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=redirect_uri
        )
        auth_url = oauth_service.get_auth_url()
        print(f"Generated auth URL: {auth_url}")
        
        # Return JSON response for the frontend
        return {"auth_url": auth_url}
        # return RedirectResponse(url=auth_url)
    except Exception as e:
        print(f"Error generating Google auth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Google login URL"
        )

@router.get("/callback")
async def google_callback(
    request: Request,
    code: str = Query(...), 
    db: AsyncSession = Depends(get_db)
):
    """Handle the OAuth callback from Google"""
    
    try:
        # For development purposes, detect if we're running locally
        host = request.headers.get("host", "")
        is_local = host.startswith("localhost") or host.startswith("127.0.0.1")
        
        # Use the correct redirect URI based on environment
        if is_local:
            redirect_uri = f"http://{host}/api/v1/auth/google/callback"
        else:
            redirect_uri = settings.GOOGLE_REDIRECT_URI
            
        print(f"Using callback redirect URI: {redirect_uri}")
        
        oauth_service = GoogleOAuthService(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=redirect_uri,
            session=db
        )
        
        # Exchange code for token
        tokens = await oauth_service.exchange_code_for_token(code)
        id_token_jwt = tokens.get("id_token")
        
        if not id_token_jwt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No ID token received from Google",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
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
        
        # Redirect to our frontend auth page with tokens
        redirect_url = f"/google-callback?access_token={auth_tokens['access_token']}&refresh_token={auth_tokens['refresh_token']}"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )