import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'interpol_notices')

    DATABASE_URL = os.getenv('DATABASE_URL',
                             'postgresql://interpol_user:interpol_pass@db:5432/interpol_db')

