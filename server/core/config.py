\
import os

# IMPORTANT: Change this in production!
# You can use environment variables for these settings for better security.
SECRET_KEY = os.getenv("SECRET_KEY", "dagiandmikessecretkey")  # Change this to a strong secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # Token validity period in minutes (1 month)

# Database URL (Example for PostgreSQL)
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")
# For SQLite, it might be something like:
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# If you have other global configurations, like API keys for external services, add them here.
# EXAMPLE_API_KEY = os.getenv("EXAMPLE_API_KEY", "your_api_key_here")
