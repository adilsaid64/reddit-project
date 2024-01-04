import numpy as np
import pandas as pd
from datetime import datetime
from .get_reddit_data import get_post_data
from .text_processor import clean_text
from .sentiment_analysis import get_sentiment

def convert_utc(utc_time):
    return datetime.utcfromtimestamp(utc_time)

def top_posts_subreddit_pipeline(subreddit_name, post_limit, comment_limmit):
    post_data = get_post_data(subreddit_name=subreddit_name, post_limit= post_limit, comment_limmit=comment_limmit)
    df = pd.DataFrame(post_data)
    df['clean_title'] = df['title'].apply(lambda x : clean_text(x))
    df['clean_selftext'] = df['selftext'].apply(lambda x : clean_text(x))
    df = get_sentiment(df, 'clean_title')
    df = get_sentiment(df, 'clean_selftext')
    df['timestamp'] = df['created_utc'].apply(convert_utc)

    return df

def comments_pipeline(df, index):
    # Get comment data from the pipeline_subreddit
    comments_df = pd.DataFrame(df['comments'][index])
    comments_df['clean_body'] = comments_df['body'].apply(lambda x : clean_text(x))
    comments_df = get_sentiment(comments_df, 'clean_body') 
    return comments_df