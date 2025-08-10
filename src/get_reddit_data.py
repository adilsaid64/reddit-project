import pandas as pd
import praw
import json
import boto3
import io
import time
from .logger_config import setup_logger
logger = setup_logger()

logger.info('Getting Reddit Credentials')
reddit_cred_file = 'src/reddit_cred.json'
with open(reddit_cred_file, 'r') as file:
    reddit_cred = json.load(file)

client_id = reddit_cred['client_id']
client_secret = reddit_cred['client_secret']
user_agent = reddit_cred['user_agent']
reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
logger.info('Got Reddit Credentials')

logger.info('Getting AWS Credentials')
aws_cred_file = 'src/aws_cred.json'
with open(aws_cred_file, 'r') as file:
    aws_creds = json.load(file)

session_id_details = {
        'access_id': aws_creds['access_id'],
        'secret_token': aws_creds['secret_token'],
        'session_token': aws_creds['session_token']
}
logger.info('Got AWS Credentials')

def stream_to_s3(bucket_name, s3_key_prefix, data, session_id_details = session_id_details):
    access_id = session_id_details.get('access_id')
    secret_token = session_id_details.get('secret_token')
    session_token = session_id_details.get('session_token')
    session = boto3.Session(
        aws_access_key_id=access_id,
        aws_secret_access_key=secret_token,
        aws_session_token=session_token
    )

    s3_client = session.client('s3')

    s3_key = f"{s3_key_prefix}/{s3_key_prefix}_{int(time.time())}.json"

    buffer = io.BytesIO()
    buffer.write(json.dumps(data).encode())
    buffer.seek(0)
    s3_client.upload_fileobj(buffer, Bucket=bucket_name, Key=s3_key)

def get_post_data(subreddit_name, post_limit = 100, comment_limmit = 100, reddit = reddit, posts_to_get = 'Top'):
    logger.info(f'Getting Reddit Data: Subreddit: {subreddit_name} --- Number of Posts: {post_limit} --- Comment Limit : {comment_limmit}')
    subreddit = reddit.subreddit(subreddit_name)
    if posts_to_get =='Top':
        logger.info('Getting top posts')
        posts = subreddit.top(limit=post_limit)  
    elif posts_to_get=='Recent':
        logger.info('Getting new posts')
        posts = subreddit.new(limit=post_limit)  
    posts_with_comments = []
    for post in posts:
        post.comments.replace_more(limit=comment_limmit)
        comments = []
        for comment in post.comments.list():
            comment_data = {
                'body': comment.body,
                'author': str(comment.author),
                'score': comment.score,
                'created_utc': comment.created_utc,
                'is_top_level': comment.is_root,
                'parent_id': comment.parent_id,
                'depth': comment.depth,
                'gilded': comment.gilded
            }
            comments.append(comment_data)

        post_data = {
            'title': post.title,
            'selftext': post.selftext,
            'score': post.score,
            'url': post.url,
            'author': str(post.author),
            'created_utc': post.created_utc,
            'num_comments': post.num_comments,
            'upvote_ratio': post.upvote_ratio,
            'subreddit': str(post.subreddit),
            'comments': comments
        }
        posts_with_comments.append(post_data)
        #stream_to_s3('reddit-project-data', subreddit_name, post_data)
    logger.info('Got Reddit Data')
    return posts_with_comments
