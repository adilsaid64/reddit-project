"""Status endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/status")  # type: ignore
def get_status():
    """Endpoint for getting service status.

    Returns:
        ServiceStatusResponse: containing readiness, and current settings
    """
    return {"message": "Hello World From The Data Processor"}