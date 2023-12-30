from logger_config import setup_logger
import pandas as pd
import praw
import json

logger = setup_logger()

logger.info('Getting Reddit Credentials')

reddit_cred_file = 'reddit_cred.json'
with open(reddit_cred_file, 'r') as file:
    reddit_cred = json.load(file)

client_id = reddit_cred['client_id']
client_secret = reddit_cred['client_secret']
user_agent = reddit_cred['user_agent']

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

logger.info('Got Credentials')

def get_post_data(subreddit_name, limit = 100, reddit = reddit):
    logger.info('Getting Reddit Data')
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(limit=limit)  
    posts_with_comments = []
    for post in top_posts:
        post.comments.replace_more(limit=None)
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

    logger.info('Got Reddit Data')
    
    return posts_with_comments
