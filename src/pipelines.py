from datetime import datetime

import pandas as pd

from .get_reddit_data import get_post_data
from .sentiment_analysis import get_sentiment
from .text_processor import clean_text


def convert_utc(utc_time):
    return datetime.utcfromtimestamp(utc_time)


def top_posts_subreddit_pipeline(
    subreddit_name, post_limit, comment_limmit, posts_to_get
):
    post_data = get_post_data(
        subreddit_name=subreddit_name,
        post_limit=post_limit,
        comment_limmit=comment_limmit,
        posts_to_get=posts_to_get,
    )
    df = pd.DataFrame(post_data)
    df["all_text"] = df["title"] + df["selftext"]
    df["clean_title"] = df["all_text"].apply(lambda x: clean_text(x))
    df = get_sentiment(df, "clean_title")
    df["timestamp"] = df["created_utc"].apply(convert_utc)

    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day

    return df


def comments_pipeline(df, comment_column, column_to_clean):
    # Get comment data from the pipeline_subreddit
    if comment_column in df.columns:
        comments_df = pd.DataFrame(df[comment_column][df.index[0]])
        if column_to_clean in comments_df.columns:
            comments_df[f"clean_{column_to_clean}"] = comments_df[
                column_to_clean
            ].apply(lambda x: clean_text(x))
            comments_df = get_sentiment(comments_df, f"clean_{column_to_clean}")
            comments_df["timestamp"] = comments_df["created_utc"].apply(convert_utc)
            return comments_df
        else:
            return comments_df
    else:
        return df
