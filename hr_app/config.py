# hr_app/config.py - load environment variables and expose DB_FILE
from dotenv import load_dotenv  # requires python-dotenv
import os

load_dotenv()  # load .env from project root
# DB_FILE environment variable with fallback to employees.db
DB_FILE = os.getenv("DB_FILE", "employees.db")