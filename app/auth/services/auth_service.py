from datetime import datetime, timedelta
from typing import Optional, List
import pyotp
import qrcode
import io
import base64
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from redis import Redis

from app.auth.models.user import User, Role, Permission, Organization
from app.auth.schemas.auth import UserCreate, TokenResponse, MFAEnrollResponse
from app.core.config import settings

class AuthService:
    def __init__(self, db: Session, redis: Redis):
        self.db = db
        self.redis = redis
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def create_user(self, user_data: UserCreate) -> User:
        # Check if user already exists
        if self.db.query(User).filter(
            (User.email == user_data.email) | 
            (User.username == user_data.username)
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Create user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=self.get_password_hash(user_data.password)
        )
        
        # If organization name provided, create or get organization
        if user_data.organization_name:
            org = self.db.query(Organization).filter(
                Organization.name == user_data.organization_name
            ).first()
            if not org:
                org = Organization(name=user_data.organization_name)
                self.db.add(org)
            db_user.organizations.append(org)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def authenticate_user(self, email: str, password: str, mfa_code: Optional[str] = None) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked until {user.locked_until}"
            )
            
        if not self.verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_MINUTES)
            self.db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
        # Check MFA if enabled
        if user.mfa_enabled:
            if not mfa_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA code required"
                )
            if not self.verify_mfa_code(user, mfa_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code"
                )
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user

    def create_tokens(self, user: User) -> TokenResponse:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = self._create_token(
            data={"sub": user.email, "type": "access"},
            expires_delta=access_token_expires
        )
        
        refresh_token = self._create_token(
            data={"sub": user.email, "type": "refresh"},
            expires_delta=refresh_token_expires
        )
        
        # Store refresh token in Redis with expiry
        self.redis.setex(
            f"refresh_token:{refresh_token}",
            int(refresh_token_expires.total_seconds()),
            user.email
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_token_expires.total_seconds())
        )

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> str:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")
            return email
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        # Verify refresh token is valid and not revoked
        email = self.verify_token(refresh_token, "refresh")
        if not self.redis.exists(f"refresh_token:{refresh_token}"):
            raise HTTPException(status_code=401, detail="Refresh token has been revoked")
            
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
            
        # Generate new token pair and invalidate old refresh token
        self.redis.delete(f"refresh_token:{refresh_token}")
        return self.create_tokens(user)

    def setup_mfa(self, user: User) -> MFAEnrollResponse:
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            user.email,
            issuer_name=settings.MFA_ISSUER_NAME
        )
        
        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert QR code to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(8)]
        
        # Store secret and hashed backup codes
        user.mfa_secret = secret
        user.mfa_enabled = True
        self.db.commit()
        
        return MFAEnrollResponse(
            secret_key=secret,
            qr_code=qr_code,
            backup_codes=backup_codes
        )

    def verify_mfa_code(self, user: User, code: str) -> bool:
        if not user.mfa_secret:
            return False
            
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(code)

    def logout(self, refresh_token: str):
        # Invalidate refresh token
        self.redis.delete(f"refresh_token:{refresh_token}")
        
    def get_user_permissions(self, user: User) -> List[str]:
        permissions = []
        for role in user.roles:
            for perm in role.permissions:
                permissions.append(f"{perm.resource}:{perm.action}")
        return permissions
