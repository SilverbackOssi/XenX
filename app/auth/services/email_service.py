import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import dotenv
dotenv.load_dotenv()

class EmailService:
    FROM_EMAIL = os.environ.get("FROM_EMAIL", "")

    # Onboarding Mails
    async def send_verification_email(self, to_email: str, verification_link: str):
        """
        Send an email verification link to users.
        """
        subject = "Verify Your Xentoba Account Email"
        html_content = f"""
        <strong>Verify Your Email Address</strong>
        <p>Thank you for registering with us. Please click the link below to verify your email address:</p>
        <p><a href="{verification_link}">{verification_link}</a></p>
        <p>If you did not register for an account, please ignore this email.</p>
        <p>Best regards,<br>The XenToba Team</p>
        """
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            print(message) # Debug
            response = sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    async def send_welcome_email(self, to_email: str):
        """
        Send a welcome email to newly registered users.
        """
        subject = "Welcome to XenToba!"
        html_content = """
        <strong>Welcome to XenToba!</strong>
        <p>Thank you for registering with us. We're excited to have you on board.</p>
        <p>Best regards,<br>The XenToba Team</p>
        """
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    
    # Authentication Mails
    async def send_login_code_email(self, to_email: str, otp_code: str):
        """
        Send a one-time password (OTP) for login.
        """
        subject = "Your One-Time Password (OTP) for Login"
        html_content = f"""
        <strong>Your One-Time Password (OTP)</strong>
        <p>You have requested to log in. Please use the following OTP to complete your login:</p>
        <h3>{otp_code}</h3>
        <p>This OTP is valid for 10 minutes. Do not share it with anyone.</p>
        <p>If you did not request this, please ignore this email.</p>
        <p>Best regards,<br>The XenToba Team</p>
        """
        
    async def send_account_recovery_email(self, to_email: str, otp_code: str, recovery_link: str | None = None):
        """
        Send an account recovery email with OTP code and optional recovery link.
        
        Args:
            to_email: Email address to send the recovery instructions to
            otp_code: The one-time password for account recovery
            recovery_link: Optional direct link to the recovery page with pre-filled values
        """
        subject = "Account Recovery Instructions"
        
        recovery_link_html = ""
        if recovery_link:
            recovery_link_html = f"""
            <p>Click the link below to reset your password:</p>
            <p><a href="{recovery_link}">Reset Your Password</a></p>
            """
            
        html_content = f"""
        <strong>Account Recovery Instructions</strong>
        <p>You have requested to recover your account. Please use the following verification code:</p>
        <h2 style="font-family: monospace; background-color: #f0f0f0; padding: 10px; text-align: center;">{otp_code}</h2>
        <p>This code is valid for 15 minutes and can be used to reset your password.</p>
        {recovery_link_html}
        <p>If you did not request account recovery, please ignore this email or contact our support team.</p>
        <p>Best regards,<br>The XenToba Team</p>
        """
        
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send account recovery email: {str(e)}")
            raise
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise
    
    async def send_password_reset_email(self, to_email: str, reset_token: int):
        """
        Send a password reset email to users.
        """
        subject = "Password Reset"
        html_content = f"""
        <strong>Password Reset</strong>
        <p>You have requested a password reset. Please use the following token to reset your password:</p>
        <h3>{reset_token}</h3>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>Best regards,<br>The XenToba Team</p>
        """
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    # Collaboration Mails
    async def send_teammate_invitation_mail(self, to_email: str, inviter_name: str, enterprise_name: str, invitation_link: str, otp: str):
        """
        Send an invitation email to a new team member.
        """
        subject = f"You're Invited to Join {enterprise_name} on XenToba!"
        html_content = f"""
        <strong>You're Invited!</strong>
        <p>Hello,</p>
        <p>{inviter_name} has invited you to join their team, <strong>{enterprise_name}</strong>, on XenToba.</p>
        <p>To accept the invitation and get started, please click the link below:</p>
        <p><a href="{invitation_link}">Join {enterprise_name}</a></p>
        <p>If you have any questions, feel free to reach out to {inviter_name}.</p>
        <p>Use this one-time password (OTP) to login to your account: <strong>{otp}</strong></p>
        <p>This OTP is valid for a limited time. Do not share it with anyone.</p>
        <p>Dont forget to change your password after logging in.</p>
        <p>If you did not request this, please ignore this email.</p>
        <p>Best regards,<br>The XenToba Team</p>
        """
        message = Mail(
            from_email=self.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(f"SendGrid Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to send invitation email: {str(e)}")
            raise
