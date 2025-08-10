import pika
import os
from dotenv import load_dotenv
from typing import Callable

def callback(ch, method, properties, body):
    print(f"Received message: {body}")

class RabbitMQConsumer:
    def __init__(self, username: str, password:str, port: int, host: str):
        self.credentials = pika.PlainCredentials(username=username, password=password)
        self.parameters = pika.ConnectionParameters(host = host, port = port, credentials=self.credentials)
        self.connection = pika.BlockingConnection(parameters=self.parameters)
        self.channel = self.connection.channel()
    
    def consume(self, queue_name:str, callback: Callable) -> None:
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

if __name__ == "__main__":
    load_dotenv()
    rabbitmq_user: str = os.getenv('RABBITMQ_USER')
    rabbitmq_password: str = os.getenv('RABBITMQ_PASSWORD')
    rabbitmq_host: str = os.getenv('RABBITMQ_HOST')
    rabbitmq_port: int = int(os.getenv('RABBITMQ_PORT'))
    rabbitmq_queue_name: int = os.getenv('RABBITMQ_QUEUE_NAME')


    rabbitmq_consumer = RabbitMQConsumer(
        rabbitmq_user, rabbitmq_password, rabbitmq_port, rabbitmq_host
    )

    rabbitmq_consumer.consume(rabbitmq_queue_name, callback)



