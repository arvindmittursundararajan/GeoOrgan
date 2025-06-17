import os
from dotenv import load_dotenv
load_dotenv()

# Application configuration
DEBUG = True
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')

# Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Application settings
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'pdf', 'png', 'jpg', 'jpeg', 'svg', 'dxf', 'dwg'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
