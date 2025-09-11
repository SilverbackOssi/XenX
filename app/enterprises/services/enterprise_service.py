from datetime import datetime, timedelta, timezone
import secrets, json
from typing import Dict, Any, Tuple, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.auth.services.email_service import EmailService
from app.auth.services.auth_service import AuthService
from app.enterprises.models.enterprises import Tentant, Staff, StaffPermission, Client
from app.enterprises.schemas.enterprise_schemas import TentantCreate, TentantResponse
from app.enterprises.schemas.staff_schemas import StaffInvitation
from app.auth.models.users import User
from app.config import get_settings

class TentantService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_enterprise_by_id(self, enterprise_id: int) -> Tuple[Optional[Tentant], Optional[str]]:
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
 
    async def create_enterprise(self, user_id: int, enterprise_data: TentantCreate):
        try:
            user = await self.db.get(User, user_id)
            if not user:
                return None, "User not found"

            new_enterprise = Tentant(
                name=enterprise_data.name,
                email=enterprise_data.email,
                type=enterprise_data.type,
                tax_year=enterprise_data.tax_year,
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

    async def invite_teammate(self, enterprise_id: int, inviter: User, invitation_data: StaffInvitation):
        try:
            # Check if the enterprise exists
            enterprise, error = await self.get_enterprise_by_id(enterprise_id)
            if error:
                return None, error

            auth_service = AuthService(self.db)
            otp=secrets.token_hex(4)  # Generate a random 4-byte OTP
            hashed_otp = auth_service.get_password_hash(otp)

            # User cannot invite themselves
            if inviter.email == invitation_data.email:
                return None, "You cannot invite yourself"

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
                permission=invitation_data.permission,
                inviter_id=inviter.id,
                invite_token=invite_token,
                invite_token_expires_at=invite_token_expires_at,
            )
            self.db.add(new_staff)
            await self.db.commit()

            # Send the invitation email
            email_service = EmailService()
            settings = get_settings()
            invitation_link = f"{settings.ACCEPT_INVITATION_URL}?token={invite_token}"

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
            
    async def invite_multiple_teammates(self, enterprise_id: int, inviter: User, invitations: list) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
            enterprise, error = await self.get_enterprise_by_id(enterprise_id)
            if error:
                return None, error

            # List to track successful invitations
            successful_invitations = []
            failed_invitations = []
            
            email_service = EmailService()
            auth_service = AuthService(self.db)

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
                        permission=invitation.permission,
                        inviter_id=inviter.id,
                        invite_token=invite_token,
                        invite_token_expires_at=invite_token_expires_at,
                    )
                    self.db.add(new_staff)
                    await self.db.commit()

                    # Send the invitation email
                    settings = get_settings()
                    invitation_link = f"{settings.ACCEPT_INVITATION_URL}?token={invite_token}"
                    
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
             
    async def update_enterprise_branding(
        self, 
        enterprise_id: int, 
        branding_data: Dict[str, Any]
    ) -> Tuple[Optional[Tentant], Optional[str]]:
        """
        Update the branding information for an enterprise.
        """
        try:
            enterprise, error = await self.get_enterprise_by_id(enterprise_id)
            if error:
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

    async def get_staff_by_id(self, enterprise_id: int, staff_id: int):
        """
        Get a staff member by ID within an enterprise.
        """
        try:
            # Check if enterprise exists
            enterprise, error = await self.get_enterprise_by_id(enterprise_id)
            if error:
                return None, "Enterprise not found"
            
            # Get staff with relationships
            stmt = select(Staff).filter_by(
                id=staff_id,
                enterprise_id=enterprise_id
            )
            result = await self.db.execute(stmt)
            staff = result.scalar_one_or_none()
            
            if not staff:
                return None, "Staff member not found in this enterprise"
                
            # Load related user data
            await self.db.refresh(staff, ["user_details"])
            
            # Prepare response data with needed relationships
            invited_staff_query = select(Staff).filter_by(
                enterprise_id=enterprise_id,
                inviter_id=staff.user_id
            )
            invited_staff_result = await self.db.execute(invited_staff_query)
            invited_staffs = invited_staff_result.scalars().all()
            
            invited_client_query = select(Client).filter_by(
                enterprise_id=enterprise_id,
                created_by=staff.user_id
            )
            invited_client_result = await self.db.execute(invited_client_query)
            invited_clients = invited_client_result.scalars().all()
            
            # Prepare StaffResponse data
            from app.enterprises.schemas.staff_schemas import StaffResponse
            
            response_data = {
                "email": staff.user_details.email,
                "role": staff.role,
                "permission": staff.permission,
                "enterprise_id": enterprise_id,
                "invited_by": staff.inviter_id or enterprise.owner_id,
                "invited_staff_ids": [s.id for s in invited_staffs],
                "invited_client_ids": [c.id for c in invited_clients]
            }
            
            return StaffResponse(**response_data), None
        except Exception as e:
            return None, str(e)
            
    async def get_all_staffs(self, enterprise_id: int):
        """
        Get all staff members of an enterprise.
        Returns a list of StaffResponse objects.
        """
        try:
            # Check if enterprise exists
            enterprise = await self.db.get(Enterprise, enterprise_id)
            if not enterprise:
                return None, "Enterprise not found"
            
            # Get all staff members with relationships
            stmt = select(Staff).filter_by(enterprise_id=enterprise_id)
            result = await self.db.execute(stmt)
            staffs = result.scalars().all()
            
            if not staffs:
                return [], None  # Return empty list instead of error if no staffs
            
            # Load related user data for each staff
            staff_responses = []
            for staff in staffs:
                await self.db.refresh(staff, ["user_details"])
                
                # Get invited staffs by this staff
                invited_staff_query = select(Staff).filter_by(
                    enterprise_id=enterprise_id,
                    inviter_id=staff.user_id
                )
                invited_staff_result = await self.db.execute(invited_staff_query)
                invited_staffs = invited_staff_result.scalars().all()
                
                # Get clients created by this staff
                invited_client_query = select(Client).filter_by(
                    enterprise_id=enterprise_id,
                    created_by=staff.user_id
                )
                invited_client_result = await self.db.execute(invited_client_query)
                invited_clients = invited_client_result.scalars().all()
                
                # Prepare StaffResponse data
                from app.enterprises.schemas.staff_schemas import StaffResponse
                
                response_data = {
                    "email": staff.user_details.email,
                    "role": staff.role,
                    "permission": staff.permission,
                    "enterprise_id": enterprise_id,
                    "invited_by": staff.inviter_id or enterprise.owner_id,
                    "invited_staff_ids": [s.id for s in invited_staffs],
                    "invited_client_ids": [c.id for c in invited_clients]
                }
                
                staff_responses.append(StaffResponse(**response_data))
            
            return staff_responses, None
        except Exception as e:
            return None, str(e)
