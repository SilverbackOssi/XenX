from datetime import datetime, timedelta, timezone
import secrets
from typing import Dict, Any, Tuple, Optional
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

    async def invite_teammate(self, enterprise_id: int, inviter: User, invitation_data: StaffInvitation, hashed_otp: str):
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
                    password_hash=hashed_otp,  # Use OTP as a temporary password
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
            invitation_link = f"http://xenx.onrender.com/accept-invitation?token={invite_token}"

            await email_service.send_teammate_invitation_mail(
                to_email=invitation_data.email,
                inviter_name=f"{inviter.first_name} {inviter.last_name}",
                enterprise_name=enterprise.name,
                invitation_link=invitation_link,
                otp=hashed_otp
            )

            return new_staff, None
        except Exception as e:
            return None, str(e)
            
    async def invite_multiple_teammates(self, enterprise_id: int, inviter: User, invitations: list, auth_service):
        """
        Invite multiple teammates to an enterprise.
        
        Args:
            enterprise_id: The ID of the enterprise
            inviter: The user sending the invitations
            invitations: List of StaffInvitationItem objects
            auth_service: AuthService instance for password hashing
            
        Returns:
            Tuple containing a list of successfully invited staff members and error message if any
        """
        try:
            # Check if the enterprise exists
            enterprise = await self.db.get(Enterprise, enterprise_id)
            if not enterprise:
                return None, "Enterprise not found"
                
            # Check if the inviter is part of the enterprise
            if enterprise.owner_id != inviter.id:
                # check if inviter is a staff member
                async with self.db.begin():
                    result = await self.db.execute(
                        select(Staff).filter_by(user_id=inviter.id, enterprise_id=enterprise_id)
                    )
                    existing_staff = result.scalar_one_or_none()
                    if not existing_staff:
                        return None, "You do not have permission to invite users to this enterprise"
            
            # List to track successful invitations
            successful_invitations = []
            failed_invitations = []
            
            email_service = EmailService()
            
            for invitation in invitations:
                try:
                    # Skip if user tries to invite themselves
                    if inviter.email == invitation.email:
                        failed_invitations.append({"email": invitation.email, "reason": "Cannot invite yourself"})
                        continue
                    
                    # Check if the user is already a staff member
                    async with self.db.begin():
                        result = await self.db.execute(
                            select(User).filter_by(email=invitation.email)
                        )
                        user = result.scalar_one_or_none()

                        if user:
                            result = await self.db.execute(
                                select(Staff).filter_by(user_id=user.id, enterprise_id=enterprise_id)
                            )
                            existing_staff = result.scalar_one_or_none()
                            if existing_staff:
                                failed_invitations.append({"email": invitation.email, "reason": "User is already a member of this enterprise"})
                                continue

                    # Generate OTP for this invitation
                    otp = secrets.token_hex(4)
                    hashed_otp = auth_service.get_password_hash(otp)
                    
                    # If user does not exist, create a new user
                    if not user:
                        # Create a new user with the provided email and OTP as password
                        new_user = User(
                            email=invitation.email,
                            username=invitation.email.split('@')[0],  # Use email prefix as username
                            is_active=False,
                            password_hash=hashed_otp,  # Use OTP as a temporary password
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
                        role=invitation.role,
                        inviter_id=inviter.id,
                        invite_token=invite_token,
                        invite_token_expires_at=invite_token_expires_at,
                    )
                    self.db.add(new_staff)
                    await self.db.commit()

                    # Send the invitation email
                    invitation_link = f"http://xenx.onrender.com/accept-invitation?token={invite_token}"

                    await email_service.send_teammate_invitation_mail(
                        to_email=invitation.email,
                        inviter_name=f"{inviter.first_name} {inviter.last_name}",
                        enterprise_name=enterprise.name,
                        invitation_link=invitation_link,
                        otp=otp
                    )

                    successful_invitations.append(new_staff)
                except Exception as e:
                    # If there's an error with one invitation, log it and continue with others
                    failed_invitations.append({"email": invitation.email, "reason": str(e)})
            
            # Return success if any invitations succeeded, or error if all failed
            if successful_invitations:
                return {"successful": successful_invitations, "failed": failed_invitations}, None
            else:
                return None, "All invitations failed"
                
        except Exception as e:
            return None, str(e)

    async def accept_invitation(self, token: str):
        try:
            async with self.db.begin():
                # Find the staff record with the given token
                result = await self.db.execute(
                    select(Staff).filter_by(invite_token=token)
                )
                staff = result.scalar_one_or_none()

                if not staff:
                    return None, "Invalid invitation token"

                # Check if the token has expired
                if staff.invite_token_expires_at < datetime.now(timezone.utc):
                    return None, "Invitation has expired"

                # Activate the staff and the user
                staff.is_active = True
                staff.invite_token = None
                staff.invite_token_expires_at = None

                user = await self.db.get(User, staff.user_id)
                if user:
                    user.is_active = True

                await self.db.commit()

            return staff, None
        except Exception as e:
            return None, str(e)
            
    async def get_enterprise_by_id(self, enterprise_id: int) -> Tuple[Optional[Enterprise], Optional[str]]:
        """
        Get an enterprise by its ID.
        """
        try:
            enterprise = await self.db.get(Enterprise, enterprise_id)
            if not enterprise:
                return None, "Enterprise not found"
                
            return enterprise, None
        except Exception as e:
            return None, str(e)
            
    async def has_permission(self, enterprise: Enterprise, user_id: int) -> bool:
        """
        Check if a user has permission to update an enterprise.
        """
        try:
            # Check if user is a superuser
            user = await self.db.get(User, user_id)
            if user and getattr(user, "is_superuser", False):
                return True

            # Check if user is the owner
            if enterprise.owner_id == user_id:
                return True
                
            # Check if user is staff with proper permissions
            result = await self.db.execute(
                select(Staff).filter_by(
                    user_id=user_id,
                    enterprise_id=enterprise.id,
                    is_active=True
                )
            )
            staff = result.scalar_one_or_none()
            
            # For now, any active staff member can update branding
            # In the future, this would be enhanced with role-based permissions
            if staff:
                return True
                
            return False
        except Exception:
            return False
            
    async def update_enterprise_branding(
        self, 
        enterprise_id: int, 
        branding_data: Dict[str, Any]
    ) -> Tuple[Optional[Enterprise], Optional[str]]:
        """
        Update the branding information for an enterprise.
        """
        try:
            enterprise = await self.db.get(Enterprise, enterprise_id)
            if not enterprise:
                return None, "Enterprise not found"
                
            # Update only the fields provided in branding_data
            for key, value in branding_data.items():
                if hasattr(enterprise, key):
                    setattr(enterprise, key, value)
            
            # Update the timestamp
            enterprise.updated_at = datetime.now(timezone.utc)
            
            await self.db.commit()
            await self.db.refresh(enterprise)
            
            return enterprise, None
        except Exception as e:
            return None, str(e)
