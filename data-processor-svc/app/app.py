"""Pre-process data service."""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers.status import router as status_router

app = FastAPI()
app.include_router(status_router)


@app.on_event("startup")  # type: ignore
async def startup_event() -> None:
    """Startup entrypoint for application."""
    # Setup logger
    access_logger = logging.getLogger("uvicorn.access")
    default_logger = logging.getLogger("uvicorn")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    if access_logger.hasHandlers():
        access_logger.handlers.clear()
    access_logger.addHandler(handler)
    if default_logger.hasHandlers():
        default_logger.handlers.clear()
    default_logger.addHandler(handler)

    app.state.logger = access_logger


@app.get("/")  # type: ignore
async def root() -> RedirectResponse:
    """Root path for the application."""
    return RedirectResponse("/status")


if __name__ == "__main__":
    uvicorn.run(app="app:app", host="0.0.0.0", port=8888, log_level="info")