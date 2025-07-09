import os
from logging import DEBUG

from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data"

DEBUG = bool(os.getenv('DEBUG') == "True")

DB_CONN = os.getenv('DB_CONN')
