from curl_cffi import requests
import time
import logging
import os
from datetime import datetime
from rabbitmq_client import RabbitMQClient
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InterpolFetcher:
    def __init__(self):
        self.config = Config()
        self.rabbitmq_client = RabbitMQClient()
        self.test_mode = os.getenv('TEST_MODE', 'false').lower() == 'true'

    def fetch_notices(self):
        try:
            if self.test_mode:
                logger.info("TEST MODE: Generating mock data")
                notices = self.generate_mock_data()
            else:
                params = {
                    'resultPerPage': self.config.RESULTS_PER_PAGE,
                    'page': 1
                }

                # curl_cffi ile Chrome browser'ı taklit et
                response = requests.get(
                    self.config.INTERPOL_API_URL,
                    params=params,
                    timeout=30,
                    impersonate="chrome124"
                )
                response.raise_for_status()

                data = response.json()
                notices = data.get('_embedded', {}).get('notices', [])

            logger.info(f"Fetched {len(notices)} notices")

            for notice in notices:
                message = {
                    'entity_id': notice.get('entity_id'),
                    'forename': notice.get('forename'),
                    'name': notice.get('name'),
                    'date_of_birth': notice.get('date_of_birth'),
                    'nationalities': notice.get('nationalities'),

                    'arrest_warrants': notice.get('arrest_warrants', []),
                    'fetch_timestamp': datetime.utcnow().isoformat()
                }

                self.rabbitmq_client.publish(message)

            return len(notices)

        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return 0

    def generate_mock_data(self):
        import random
        mock_notices = []
        names = [
            ('John', 'Doe'), ('Jane', 'Smith'), ('Ahmad', 'Hassan'),
            ('Maria', 'Garcia'), ('Vladimir', 'Petrov')
        ]

        for i in range(5):
            forename, name = random.choice(names)
            mock_notices.append({
                'entity_id': f'{random.randint(2020, 2025)}/{random.randint(10000, 99999)}',
                'forename': forename,
                'name': name,
                'date_of_birth': f'{random.randint(1970, 2000)}/{random.randint(1, 12):02d}/{random.randint(1, 28):02d}',
                'nationalities': [random.choice(['US', 'GB', 'FR', 'DE'])],
                'arrest_warrants': []
            })
        return mock_notices

    def run(self):
        logger.info("Interpol Fetcher started")

        try:
            while True:
                logger.info("Starting fetch cycle")
                count = self.fetch_notices()
                logger.info(f"Fetch cycle completed. Processed {count} notices")

                logger.info(f"Sleeping for {self.config.FETCH_INTERVAL} seconds")
                time.sleep(self.config.FETCH_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Shutting down gracefully")
        finally:
            self.rabbitmq_client.close()


if __name__ == "__main__":
    fetcher = InterpolFetcher()
    fetcher.run()
