"""Fetch data endpoint."""

from fastapi import APIRouter
from schema.request import FetchDataRequestPayload
from schema.response import FetchDataResponsePayload
from src.get_reddit_data import get_post_data
from src.pipelines import data_cleaning_pipeline
router = APIRouter()

@router.post("/get_data")  # type: ignore
def get_data(payload: FetchDataRequestPayload):
    """Endpoint for getting reddit data frm a subredit"""

    reddit_data = get_post_data(
        subreddit_name=payload.subreddit_name,
        post_limit=payload.post_limit,
        comment_limmit=payload.comment_limit,
        posts_to_get=payload.posts_to_get
    )

    processed_data = data_cleaning_pipeline(
        post_data = reddit_data
    )

    # call comment cleaning pipeline

    # call sentiment analysis endpoint here with processeddata

    return FetchDataResponsePayload(data = ...)