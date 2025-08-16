from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    # In production, these would come from environment variables
    SMTP_HOST = "localhost"
    SMTP_PORT = 1025  # Default port for development SMTP server
    SMTP_USER = ""
    SMTP_PASSWORD = ""
    FROM_EMAIL = "noreply@xentoba.com"

    async def send_welcome_email(self, to_email: str):
        """
        Send a welcome email to newly registered users.
        """
        msg = MIMEMultipart()
        msg['From'] = self.FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = "Welcome to XenToba!"

        body = """
        Welcome to XenToba!

        Thank you for registering with us. We're excited to have you on board.

        Best regards,
        The XenToba Team
        """
        msg.attach(MIMEText(body, 'plain'))

        try:
            async with SMTP(hostname=self.SMTP_HOST, port=self.SMTP_PORT) as smtp:
                if self.SMTP_USER and self.SMTP_PASSWORD:
                    await smtp.login(self.SMTP_USER, self.SMTP_PASSWORD)
                await smtp.send_message(msg)
        except Exception as e:
            # In production, this should be properly logged
            print(f"Failed to send email: {str(e)}")
            raise
