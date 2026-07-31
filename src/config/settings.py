import os
from dotenv import load_dotenv


load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY",'')


APP_ENV = os.getenv('APP_ENV','development')


def check_settings():


    if not DEEPSEEK_API_KEY:
        raise ValueError('DEEPSEEK_API_KEY is missing')