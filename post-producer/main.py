from abc import ABC, abstractmethod
import praw
import datetime
import json
from dotenv import load_dotenv
import os
from typing import Generator
import logging 
from dataclasses import dataclass, asdict

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


if __name__ == '__main__':
    load_dotenv()
    reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
    reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    reddit_user_agent = os.getenv('REDDIT_USER_AGENT')
    subreddit = os.getenv('SUB_REDDIT')

    reddit_fetcher = RedditFetcher(
        reddit_client_id, 
        reddit_client_secret, 
        reddit_user_agent,
        subreddit,
        )
    
    for post in reddit_fetcher.fetch_data():
        logging.info(json.dumps(post.title, indent=2))

