import os

from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data"

DEBUG = bool(os.getenv('DEBUG') == "True")
DB_CONN = os.getenv('DB_CONN')
DB_CREATE = bool(os.getenv('DB_CREATE') == 'True')
SUGGEST_TOKEN = os.getenv('SUGGEST_TOKEN')
SUGGEST_URL = os.getenv('SUGGEST_URL')
USER_SECRET = os.getenv('USER_SECRET')
USER_LIFESPAN = int(os.getenv('USER_LIFESPAN'))
POST_URL = os.getenv('POST_URL')
POST_API_TIMEOUT = int(os.getenv('POST_API_TIMEOUT'))