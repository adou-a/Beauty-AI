import os
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY",'')

APP_ENV = os.getenv('APP_ENV','development')


def check_settings():


    if not OPENAI_API_KEY:
        raise ValueError('OPENAI_API_KEY is missing')