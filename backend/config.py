import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
MONGO_URI = os.getenv("MONGO_URI")

# Mail config — uncomment when OTP is ready
# MAIL_EMAIL = os.getenv("MAIL_EMAIL")
# MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")