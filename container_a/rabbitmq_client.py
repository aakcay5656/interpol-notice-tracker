import pika
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self):
        self.config = Config()
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        try:
            credentials = pika.PlainCredentials(
                self.config.RABBITMQ_USER,
                self.config.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=self.config.RABBITMQ_HOST,
                port=self.config.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.config.RABBITMQ_QUEUE, durable=True)
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish(self, message):
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()

            self.channel.basic_publish(
                exchange='',
                routing_key=self.config.RABBITMQ_QUEUE,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            logger.info(f"Message published: {message.get('entity_id', 'unknown')}")
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            self.connect()
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
