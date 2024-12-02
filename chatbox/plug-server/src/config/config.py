import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

env = os.environ.get("FLASK_ENV")

# FLASK CONFIG
MAX_CONTENT_LENGTH = int(os.environ.get(
    "MAX_CONTENT_LENGTH", 104857600))  # default 100 MB
TIMEOUT = int(os.environ.get("TIMEOUT", 300))  # default 5 minutes

SECRET_KEY = os.environ.get("SECRET_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# JWT secret
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(
    days=15) if env == "development" else timedelta(minutes=20)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
JWT_COOKIE_CSRF_PROTECT = True
JWT_TOKEN_LOCATION = ["cookies"]
JWT_SESSION_COOKIE = False
# if true csrf will be saved as cookies else will remain in server and can be accessed using flask_jwt_extended.get_csrf_token()
JWT_CSRF_IN_COOKIES = True

# SMTP Mail
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_PORT = os.environ.get("SMTP_PORT")
SMTP_SENDER_MAIL = os.environ.get("SMTP_SENDER_MAIL")
SMTP_SENDER_PASSWORD = os.environ.get("SMTP_SENDER_PASSWORD")

# APPROVED EMAILS
LIVE_DEMO_APPROVER_MAIL = os.environ.get("LIVE_DEMO_APPROVER_MAIL")

# STRIPE
STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY = os.environ.get(
    "STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY")
STRIPE_API_SECRET_KEY = os.environ.get("STRIPE_API_SECRET_KEY")

# ROLES
ADMIN = "1"
USER = "0"

# SUBSCRIPTION
UPLOAD_FILES = os.environ.get("UPLOAD_FILES")
CRAWL_WEBSITE = os.environ.get("CRAWL_WEBSITE")
SAVE_CONVERSATION = os.environ.get("SAVE_CONVERSATION")
API_ACCESS = os.environ.get("API_ACCESS")
CUSTOMIZE_CLIENT = os.environ.get("CUSTOMIZE_CLIENT")

# URL
URL_API_BE = os.getenv('URL_API_BE')
URL_API_FE = os.getenv('URL_API_FE')

BASE_URL = f'{URL_API_BE}{os.getenv("BASE_URL")}'
IMAGE_BASE_URL = f'{URL_API_BE}{os.getenv("IMAGE_BASE_URL")}'
TERM_URL = f'{URL_API_FE}{os.getenv("TERM_URL")}'
PRIVACY_URL = f'{URL_API_FE}{os.getenv("PRIVACY_URL")}'
WEBSITE_URL = f'{URL_API_FE}{os.getenv("WEBSITE_URL")}'

# APIFY
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")

# CHROMADB
WEB_ORIGIN = os.environ.get("WEB_ORIGIN")

# subscription limits
FREE_UPLOAD_FILE = os.environ.get("FREE_UPLOAD_FILE")
FREE_CRAWL_WEBSITE = os.environ.get("FREE_CRAWL_WEBSITE")

STARTER_UPLOAD_FILE = os.environ.get("STARTER_UPLOAD_FILE")
STARTER_CRAWL_WEBSITE = os.environ.get("STARTER_CRAWL_WEBSITE")

PRO_UPLOAD_FILE = os.environ.get("PRO_UPLOAD_FILE")
PRO_CRAWL_WEBSITE = os.environ.get("PRO_CRAWL_WEBSITE")

COMPANY_UPLOAD_FILE = os.environ.get("COMPANY_UPLOAD_FILE")
COMPANY_CRAWL_WEBSITE = os.environ.get("COMPANY_CRAWL_WEBSITE")
NOMIC_API_KEY = os.environ.get("NOMIC_API_KEY")

ROUTE_PARAMETER_ALLOWED = os.environ.get("ROUTE_PARAMETER_ALLOWED")

# URL PATH
URL_PATH = ""
DEFAULT_BILLING_CALL_BACK_URL = "https://webaipilot.ca"
# dev or prod
if env == "production":
    JWT_COOKIE_SAMESITE = "None"
    JWT_COOKIE_DOMAIN = "webaipilot.ca"
    JWT_COOKIE_SECURE = True  # true in production
    STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY = os.environ.get(
        "STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY_SERVER")
    BASE_URL = os.environ.get("BASE_URL_SERVER")
    DEFAULT_BILLING_CALL_BACK_URL = "https://webaipilot.ca"
    STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY = os.environ.get(
        "STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY_SERVER_LIVE")
    STRIPE_API_SECRET_KEY = os.environ.get("STRIPE_API_SECRET_KEY_LIVE")
elif env == "staging":
    JWT_COOKIE_SAMESITE = "None"
    JWT_COOKIE_DOMAIN = "webaipilot.ca"
    JWT_COOKIE_SECURE = True  # true in production
    STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY = os.environ.get(
        "STRIPE_ENDPOINTS_WEBHOOK_SECRET_KEY_STAGING_SERVER")
    BASE_URL = os.environ.get("BASE_URL_STAGING_SERVER")
    TERM_URL = "https://webaipilot.ca/index.html#/term"
    PRIVACY_URL = "https://webaipilot.ca/index.html#/privacy-policy"
    WEBSITE_URL = "https://webaipilot.ca/index.html#/home"
    URL_PATH = "/stage"
    DEFAULT_BILLING_CALL_BACK_URL = "https://webaipilot.ca/home"
elif env == "docker":
    JWT_COOKIE_SECURE = False
    BASE_URL_DOCKER = os.environ.get("BASE_URL_STAGING_SERVER")
BASE_URL_DOCKER = os.environ.get("BASE_URL_STAGING_SERVER")
