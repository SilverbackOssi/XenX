from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.services.email_service import EmailService
from app.enterprises.models.enterprises import Enterprise
from app.enterprises.schemas.enterprise_schemas import EnterpriseCreate, EnterpriseResponse
from app.enterprises.schemas.staff_schemas import StaffInvitation
from app.auth.models.users import Staff, User

class EnterpriseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_enterprise(self, user_id: int, enterprise_data: EnterpriseCreate):
        try:
            user = await self.db.get(User, user_id)
            if not user:
                return None, "User not found"

            new_enterprise = Enterprise(
                name=enterprise_data.name,
                email=enterprise_data.email,
                type=enterprise_data.type,
                default_tax_year=enterprise_data.default_tax_year,
                country=enterprise_data.country,
                city=enterprise_data.city,
                description=getattr(enterprise_data, "description", None),
                website=getattr(enterprise_data, "website", None),
                owner_id=user_id
            )


            self.db.add(new_enterprise)
            await self.db.commit()
            await self.db.refresh(new_enterprise)

            return new_enterprise, None
        except Exception as e:
            return None, str(e)


    async def invite_teammate(self, enterprise_id: int, inviter: User, invitation_data: StaffInvitation, otp: str):
        try:
            # Check if the enterprise exists
            enterprise = await self.db.get(Enterprise, enterprise_id)
            if not enterprise:
                return None, "Enterprise not found"
            
            # User cannot invite themselves
            if inviter.email == invitation_data.email:
                return None, "You cannot invite yourself"

            # Check if the inviter is part of the enterprise
            if enterprise.owner_id != inviter.id:
                # XXX add permission levels and check for permissions
                
                # check if inviter is a staff member
                async with self.db.begin():
                    result = await self.db.execute(
                        select(Staff).filter_by(user_id=inviter.id, enterprise_id=enterprise_id)
                    )
                    existing_staff = result.scalar_one_or_none()
                    if not existing_staff:
                        return None, "You do not have permission to invite users to this enterprise"

            # Check if the user is already a staff member
            async with self.db.begin():
                result = await self.db.execute(
                    select(User).filter_by(email=invitation_data.email)
                )
                user = result.scalar_one_or_none()

                if user:
                    result = await self.db.execute(
                        select(Staff).filter_by(user_id=user.id, enterprise_id=enterprise_id)
                    )
                    existing_staff = result.scalar_one_or_none()
                    if existing_staff:
                        return None, "User is already a member of this enterprise"

            

            # If user does not exist, create a new user
            if not user:
                # Create a new user with the provided email and OTP as password
                new_user = User(
                    email=invitation_data.email,
                    username=invitation_data.email.split('@')[0],  # Use email prefix as username
                    is_active=False,
                    password_hash=otp,  # Use OTP as a temporary password
                )
                self.db.add(new_user)
                await self.db.commit()
                await self.db.refresh(new_user)
                user = new_user

            # Generate an invitation token
            invite_token = secrets.token_urlsafe(32)
            invite_token_expires_at = datetime.now(timezone.utc) + timedelta(days=7)

            # Create a new staff record
            new_staff = Staff(
                user_id=user.id,
                enterprise_id=enterprise_id,
                role=invitation_data.role,
                inviter_id=inviter.id,
                invite_token=invite_token,
                invite_token_expires_at=invite_token_expires_at,
            )
            self.db.add(new_staff)
            await self.db.commit()

            # Send the invitation email
            email_service = EmailService()
            invitation_link = f"http://localhost:3000/accept-invitation?token={invite_token}" # Replace with your frontend URL
            

            await email_service.send_teammate_invitation_mail(
                to_email=invitation_data.email,
                inviter_name=f"{inviter.first_name} {inviter.last_name}",
                enterprise_name=enterprise.name,
                invitation_link=invitation_link,
                otp=otp
            )

            return new_staff, None
        except Exception as e:
            return None, str(e)
