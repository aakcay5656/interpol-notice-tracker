import pika
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self, callback):
        self.config = Config()
        self.callback = callback
        self.connection = None
        self.channel = None

    def connect(self):
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
        logger.info("RabbitMQ consumer connected")

    def consume(self):
        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                logger.info(f"Received message: {message.get('entity_id', 'unknown')}")
                self.callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.config.RABBITMQ_QUEUE,
            on_message_callback=on_message
        )

        logger.info("Started consuming messages")
        self.channel.start_consuming()
