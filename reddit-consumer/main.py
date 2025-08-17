import os, json, requests, pika
from dotenv import load_dotenv
from pymongo import MongoClient



def get_inference(url: str, text: str) -> dict[str, dict[str, str | int]]:
    resp = requests.post(url, json={"text": text}, timeout=10)
    resp.raise_for_status()
    return resp.json()

class MongoLogger:
    def __init__(self, uri="mongodb://mongo:27017", db_name="redditPosts", collection="posts"):
        self.client = MongoClient(uri)                # one client for the whole process
        self.collection = self.client[db_name][collection]

    def log(self, doc: dict) -> None:
        self.collection.insert_one(doc)

def make_callback(mongo: MongoLogger, ml_url: str):
    def callback(ch, method, properties, body: bytes):
        try:
            data = json.loads(body.decode("utf-8"))
            # Add subreddit from queue name
            data["subreddit"] = method.routing_key
            data["title_sentiment"] = get_inference(ml_url, data.get("title", ""))['inference']
            data["selftext_sentiment"] = get_inference(ml_url, data.get("selftext", ""))['inference']

            mongo.log(data)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"processing error: {e!r}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    return callback

class RabbitMQConsumer:
    def __init__(self, username: str, password: str, port: int, host: str):
        creds = pika.PlainCredentials(username=username, password=password)
        params = pika.ConnectionParameters(host=host, port=port, credentials=creds)
        self.conn = pika.BlockingConnection(params)
        self.channel = self.conn.channel()

    def consume(self, queue_name: str, cb):
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=5)
        self.channel.basic_consume(queue=queue_name, on_message_callback=cb, auto_ack=False)
        self.channel.start_consuming()

if __name__ == "__main__":
    load_dotenv()
    rabbitmq_user = os.getenv("RABBITMQ_USER")
    rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")
    rabbitmq_host = os.getenv("RABBITMQ_HOST")
    rabbitmq_port = int(os.getenv("RABBITMQ_PORT"))
    rabbitmq_queue_name = os.getenv("RABBITMQ_QUEUE_NAME")


    ml_url = os.getenv("ML_INFERENCE_URL")


    mongo = MongoLogger(uri=os.getenv("MONGODB_URI", "mongodb://mongo:27017"),
                        db_name="redditPosts",
                        collection="posts")

    consumer = RabbitMQConsumer(rabbitmq_user, rabbitmq_password, rabbitmq_port, rabbitmq_host)
    consumer.consume(rabbitmq_queue_name, make_callback(mongo, ml_url))
