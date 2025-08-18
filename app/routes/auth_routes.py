from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.database import get_db
from app.schemas.schema import UserCreate, UserResponse
from app.auth.services.auth_service import AuthService
from app.auth.models.user import UserRole
from app.auth.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user, error = await auth_service.create_user(
        email=user_data.email,
        username=user_data.username,
        password=user_data.password,
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )

    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )

    # Send welcome email (async)
    '''try:
        email_service = EmailService()

        if user and hasattr(user, "email"):
            await email_service.send_welcome_email(user_data.email)
        else:
            print("User email is not available or not a string, skipping welcome email.")
    except Exception as e:
        # Log the error but don't fail registration
        print(f"Failed to send welcome email: {str(e)}")
'''
    return user
