FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY . .

RUN uv sync --verbose

EXPOSE 8000

CMD ["uv", "run", "main.py"]
