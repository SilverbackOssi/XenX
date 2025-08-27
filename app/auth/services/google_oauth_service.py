from typing import Dict, Any, Optional, Tuple
from google.oauth2 import id_token
from google.auth.transport import requests
import httpx
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models.users import User
from app.auth.services.auth_service import AuthService
import secrets
from datetime import datetime, timezone
import string
import random
import urllib.parse


class GoogleOAuthService:
    def __init__(self, 
                 client_id: str, 
                 client_secret: str,
                 redirect_uri: str,
                 session: Optional[AsyncSession] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session = session
        self.auth_service = AuthService(session) if session else None
    
    def get_auth_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        # Properly URL encode all parameters
        encoded_params = urllib.parse.urlencode(params)
        return f"https://accounts.google.com/o/oauth2/auth?{encoded_params}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        print(f"Exchanging code for token with redirect_uri: {self.redirect_uri}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri,
                        "grant_type": "authorization_code"
                    }
                )
                
                if response.status_code != 200:
                    print(f"OAuth token exchange failed: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Failed to exchange authorization code: {response.text}",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                    
                return response.json()
                
        except Exception as e:
            print(f"OAuth token exchange error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"OAuth token exchange failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to exchange authorization code",
                    headers={"WWW-Authenticate": "Bearer"}
                )
                
            return response.json()
    
    async def get_user_info(self, id_token_jwt: str) -> Dict[str, Any]:
        """Verify and decode the ID token to get user info"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                id_token_jwt, 
                requests.Request(), 
                self.client_id
            )
            
            # Check issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
                
            return idinfo
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid ID token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    async def authenticate_or_create_user(self, user_info: Dict[str, Any]) -> Tuple[User, str]:
        """Find existing user or create a new one based on Google profile"""
        if not self.session or not self.auth_service:
            raise ValueError("Session and AuthService must be provided")
            
        # Try to find user by email
        user = await self.auth_service.get_user_by_email(user_info["email"])
        
        # If user exists, update Google info and return
        if user:
            # Update Google-specific fields if needed
            user.google_id = user_info.get("sub")
            user.email_verified = True  # Google emails are verified
            user.last_login = datetime.now(timezone.utc)
            await self.session.commit()
            return user, ""
        
        # Create new user
        # Extract username from email or create one
        username = user_info.get("email").split("@")[0]
        # Ensure username is unique by appending digits if needed
        base_username = username
        suffix = 1
        while await self.auth_service.get_user_by_username(username):
            username = f"{base_username}{suffix}"
            suffix += 1
            
        user, error = await self.auth_service.create_user_from_google(
            email=user_info.get("email"),
            username=username,
            first_name=user_info.get("given_name"),
            last_name=user_info.get("family_name"),
        )
        
        if user:
            # Set Google-specific fields
            user.google_id = user_info.get("sub")
            user.email_verified = True  # Google emails are verified
            user.last_login = datetime.now(timezone.utc)
            await self.session.commit()
            
        return user, error