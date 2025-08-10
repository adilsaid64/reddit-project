FROM ghcr.io/astral-sh/uv:debian-slim

WORKDIR /app

COPY . /app

RUN cd app && uv sync --verbose

EXPOSE 8888

CMD ["uv", "run", "main.py"]