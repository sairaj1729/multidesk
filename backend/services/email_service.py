import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from config import settings
from db import get_database
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.MAIL_HOST
        self.smtp_port = settings.MAIL_PORT
        self.smtp_user = settings.MAIL_USER
        self.smtp_pass = settings.MAIL_PASS
        self.mail_from = settings.MAIL_FROM

    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.mail_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'html'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.smtp_user, self.smtp_pass)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.mail_from, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_otp_email(self, email: str, otp: str, purpose: str = "verification") -> bool:
        """Send OTP email for verification"""
        subject = f"Multi Desk - Your OTP for {purpose.title()}"
        
        body = f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #3b82f6; margin: 0;">Multi Desk</h1>
                    <p style="color: #6b7280; margin: 5px 0 0 0;">Dashboard & Task Management</p>
                </div>
                
                <div style="background-color: #f8fafc; padding: 30px; border-radius: 8px; margin: 20px 0;">
                    <h2 style="color: #1f2937; margin-top: 0;">Your OTP Code</h2>
                    <p style="color: #4b5563; line-height: 1.6;">
                        Your OTP for {purpose} is:
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="display: inline-block; background-color: #3b82f6; color: white; padding: 15px 30px; font-size: 24px; font-weight: bold; letter-spacing: 3px; border-radius: 8px;">{otp}</span>
                    </div>
                    <p style="color: #6b7280; font-size: 14px; text-align: center;">
                        This OTP will expire in {settings.OTP_EXPIRE_MINUTES} minutes.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                        If you didn't request this OTP, please ignore this email.
                    </p>
                    # <p style="color: #9ca3af; font-size: 12px; margin: 5px 0 0 0;">
                    #     © 2024 Multi Desk. All rights reserved.
                    # </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(email, subject, body)

    async def store_otp(self, email: str, otp: str, purpose: str = "verification") -> bool:
        """Store OTP in database"""
        try:
            db = get_database()
            otp_collection = db.otps
            
            # Set expiry time
            expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
            
            # Store OTP (replace existing OTP for same email and purpose)
            await otp_collection.update_one(
                {"email": email, "purpose": purpose},
                {
                    "$set": {
                        "email": email,
                        "otp": otp,
                        "purpose": purpose,
                        "expires_at": expires_at,
                        "created_at": datetime.utcnow(),
                        "verified": False
                    }
                },
                upsert=True
            )
            
            logger.info(f"OTP stored for {email} with purpose {purpose}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store OTP for {email}: {e}")
            return False

    async def verify_otp(self, email: str, otp: str, purpose: str = "verification") -> bool:
        """Verify OTP"""
        try:
            db = get_database()
            otp_collection = db.otps
            
            # Find valid OTP
            otp_doc = await otp_collection.find_one({
                "email": email,
                "otp": otp,
                "purpose": purpose,
                "verified": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if otp_doc:
                # Mark OTP as verified
                await otp_collection.update_one(
                    {"_id": otp_doc["_id"]},
                    {"$set": {"verified": True, "verified_at": datetime.utcnow()}}
                )
                logger.info(f"OTP verified successfully for {email}")
                return True
            else:
                logger.warning(f"Invalid or expired OTP for {email}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to verify OTP for {email}: {e}")
            return False

    async def send_verification_otp(self, email: str) -> Optional[str]:
        """Generate and send verification OTP"""
        try:
            otp = self.generate_otp()
            
            # Store OTP in database
            if await self.store_otp(email, otp, "verification"):
                # Send email
                if await self.send_otp_email(email, otp, "verification"):
                    return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send verification OTP to {email}: {e}")
            return None

    async def send_password_reset_otp(self, email: str) -> Optional[str]:
        """Generate and send password reset OTP"""
        try:
            otp = self.generate_otp()
            
            # Store OTP in database
            if await self.store_otp(email, otp, "password_reset"):
                # Send email
                if await self.send_otp_email(email, otp, "password reset"):
                    return otp
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to send password reset OTP to {email}: {e}")
            return None

# Create global email service instance
email_service = EmailService()