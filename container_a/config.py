import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'interpol_notices')

    INTERPOL_API_URL = os.getenv('INTERPOL_API_URL',
                                 'https://ws-public.interpol.int/notices/v1/red')
    FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', 300))
    RESULTS_PER_PAGE = int(os.getenv('RESULTS_PER_PAGE', 20))
