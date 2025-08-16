FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY . .

RUN uv sync --verbose

CMD ["uv", "run", "main.py"]