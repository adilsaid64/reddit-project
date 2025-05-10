"""Fetch data endpoint."""

from fastapi import APIRouter
from typing import Any, Literal
from pydantic import BaseModel, Field
from src.get_reddit_data import get_post_data
router = APIRouter()

class FetchDataRequestPayload(BaseModel):
    """Fetch data request payload"""

    subreddit_name: str = Field(description="Subreddit to fetch")
    post_limit: int = Field(description="Maximum number of posts")
    comment_limit: int = Field(description="Max comments per post")
    posts_to_get: Literal["Top", "Recent"] = Field(description="Get TOp posts from reddit or recent")

class FetchDataResponsePayload(BaseModel):
    """Fetch data response payload"""
    data: dict[str, str | int | float | list[dict[str, str | int | float ]]] = Field("Reddit data with comments")

@router.post("/get_data")  # type: ignore
def get_data(payload: FetchDataRequestPayload):
    """Endpoint for getting reddit data frm a subredit"""

    reddit_data = get_post_data(
        subreddit_name=payload.subreddit_name,
        post_limit=payload.post_limit,
        comment_limmit=payload.comment_limit,
        posts_to_get=payload.posts_to_get
    )

    # call reddit post cleaning pipeline
    # call comment cleaning pipeline

    # return
    

    return FetchDataResponsePayload(data = ...)