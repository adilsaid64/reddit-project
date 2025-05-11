from pydantic import BaseModel, Field

class FetchDataResponsePayload(BaseModel):
    """Fetch data response payload"""
    data: dict[str, str | int | float | list[dict[str, str | int | float ]]] = Field("Reddit data with comments")
