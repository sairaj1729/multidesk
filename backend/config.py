import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # FastAPI Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "multidesk")
    
    # Email Configuration
    MAIL_HOST: str = os.getenv("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USER: str = os.getenv("MAIL_USER", "")
    MAIL_PASS: str = os.getenv("MAIL_PASS", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    
    # Resend Configuration
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_SENDER_EMAIL: str = os.getenv("RESEND_SENDER_EMAIL", "onboarding@resend.dev")
    
    # OTP Configuration
    OTP_EXPIRE_MINUTES: int = int(os.getenv("OTP_EXPIRE_MINUTES", "10"))
    
    # OTP Bypass Configuration
    BYPASS_OTP_VERIFICATION: bool = os.getenv("BYPASS_OTP_VERIFICATION", "false").lower() == "true"
    
    # Jira Configuration
    JIRA_DOMAIN: str = os.getenv("JIRA_DOMAIN", "")
    JIRA_EMAIL: str = os.getenv("JIRA_EMAIL", "")
    JIRA_API_TOKEN: str = os.getenv("JIRA_API_TOKEN", "")

    FERNET_KEY: str = os.getenv("FERNET_KEY")
    

    
    # Updated MongoDB Configuration for new structure
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "multiDeskDB")

    @property
    def JIRA_BASE_URL(self) -> str:
        return f"https://{self.JIRA_DOMAIN}"

settings = Settings()

print("FERNET KEY LOADED:", bool(settings.FERNET_KEY))