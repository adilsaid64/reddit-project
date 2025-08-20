import praw
import datetime
import json
from dotenv import load_dotenv
import os
from typing import Generator
import logging 
from dataclasses import dataclass, asdict
import pika
import time
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s'
)

@dataclass()
class RedditPost:
    title: str
    id: str
    url: str
    created_utc: float
    selftext: str
    now_time: float

class RedditFetcher:
    def __init__(self, client_id:str, client_secret:str, user_agent:str, subreddit:str):
        self.reddit = praw.Reddit(
            client_id = client_id,
            client_secret = client_secret,
            user_agent = user_agent
        )
        self.subreddit = subreddit


    def fetch_data(self)->Generator[RedditPost, None, None]:
        subreddit = self.reddit.subreddit(self.subreddit)
        for submission in subreddit.stream.submissions(skip_existing = True):
            yield RedditPost(
                title=submission.title,
                id=submission.id,
                url=submission.url,
                created_utc=submission.created_utc,
                selftext=submission.selftext,
                now_time=datetime.datetime.now().timestamp(),
            )

class MockRedditFetcher:
    """Simulates fetching Reddit posts without hitting Reddit's API."""
    def __init__(self, client_id: str, client_secret: str, user_agent: str, subreddit: str):
        self.subreddit = subreddit

    def fetch_data(self) -> Generator["RedditPost", None, None]:
        i: int = 0
        base_titles: list[str] = [
            "This community is amazing!",
            "This is so disappointing.",
            "What an incredible achievement!",
            "Why does this keep happening?",
            "I love how helpful everyone is here.",
            "I can't believe how bad this is."
        ]

        selftexts: list[str] = [
            "I'm feeling so inspired after reading these comments.",
            "I'm frustrated with the lack of progress.",
            "This made my day!",
            "This situation is really discouraging.",
            "The advice here has really helped me grow.",
            "I feel let down by the outcome."
        ]

        while True:
            yield RedditPost(
                title=f"{random.choice(base_titles)} - {i}",
                id=f"id_{i}",
                url=f"http://example.com/{i}",
                created_utc=datetime.datetime.now().timestamp(),
                selftext=random.choice(selftexts),
                now_time=datetime.datetime.now().timestamp(),
            )
            i += 1

class RabbitMQPublisher:
    def __init__(self, username: str, password:str, port: int, host: str):
        self.credentials = pika.PlainCredentials(username=username, password=password)
        self.parameters = pika.ConnectionParameters(host = host, port = port, credentials=self.credentials)
        self.connection = pika.BlockingConnection(parameters=self.parameters)
        self.channel = self.connection.channel()
    
    def publish(self, queue_name:str, message: str) -> None:
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(exchange='',
                                   routing_key=queue_name,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,
                                   ))
    
if __name__ == '__main__':
    load_dotenv()
    reddit_client_id: str = os.getenv('REDDIT_CLIENT_ID')
    reddit_client_secret: str = os.getenv('REDDIT_CLIENT_SECRET')
    reddit_user_agent: str = os.getenv('REDDIT_USER_AGENT')
    subreddit: str = os.getenv('SUB_REDDIT')

    rabbitmq_user: str = os.getenv('RABBITMQ_USER')
    rabbitmq_password: str = os.getenv('RABBITMQ_PASSWORD')
    rabbitmq_host: str = os.getenv('RABBITMQ_HOST')
    rabbitmq_port: int = int(os.getenv('RABBITMQ_PORT'))
    simulation_mode: bool = os.getenv('SIMULATION_MODE')

    if simulation_mode==True:
        reddit_fetcher = MockRedditFetcher(
            reddit_client_id, 
            reddit_client_secret, 
            reddit_user_agent,
            subreddit,
            )
    else:
        reddit_fetcher = RedditFetcher(
            reddit_client_id, 
            reddit_client_secret, 
            reddit_user_agent,
            subreddit,
            )

    
    rabbitmq_publisher = RabbitMQPublisher(
        rabbitmq_user, rabbitmq_password, rabbitmq_port, rabbitmq_host
    )

    for post in reddit_fetcher.fetch_data():
        rabbitmq_publisher.publish(subreddit, json.dumps(asdict(post)))
        logging.info(json.dumps(asdict(post)))
        time.sleep(2)
