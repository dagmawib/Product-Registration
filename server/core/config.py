\
import os

# IMPORTANT: Change this in production!
# You can use environment variables for these settings for better security.
SECRET_KEY = os.getenv("SECRET_KEY", "dagiandmikessecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Use environment variable
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # Use environment variable, cast to int, ensure default is string

# Database URL (Example for PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")  # Uncommented and ensure it's read

# If you have other global configurations, like API keys for external services, add them here.
# EXAMPLE_API_KEY = os.getenv("EXAMPLE_API_KEY", "your_api_key_here")

# For allowed_origins, if you plan to use it from config.py for CORS:
# ALLOWED_ORIGINS_STRING = os.getenv("allowed_origins", "*")
# ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_STRING.split(',')]
