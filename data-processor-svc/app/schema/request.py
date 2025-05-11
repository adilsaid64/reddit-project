from pydantic import BaseModel, Field
from typing import Literal

class FetchDataRequestPayload(BaseModel):
    """Fetch data request payload"""

    subreddit_name: str = Field(description="Subreddit to fetch")
    post_limit: int = Field(description="Maximum number of posts")
    comment_limit: int = Field(description="Max comments per post")
    posts_to_get: Literal["Top", "Recent"] = Field(description="Get TOp posts from reddit or recent")