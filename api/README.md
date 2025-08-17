# Sentiment Dashboard API

A FastAPI-based API that provides real-time sentiment data for the Reddit sentiment analysis dashboard.

## Features

- **Real-time data polling** from MongoDB
- **Sentiment analysis metrics** with time-based filtering
- **Subreddit statistics** and aggregation
- **Health monitoring** and Prometheus metrics
- **CORS support** for dashboard integration

## API Endpoints

### Health Check
- `GET /health` - Check API and MongoDB connection status

### Main Data Endpoints
- `GET /recent-data?hours=24` - Get recent posts with sentiment data (default: last 24 hours)
- `GET /sentiment-summary?hours=24` - Get aggregated sentiment statistics
- `GET /subreddit-stats?hours=24` - Get statistics grouped by subreddit

### Monitoring
- `GET /metrics` - Prometheus metrics for monitoring

## Data Models

### RedditPost
```json
{
  "id": "string",
  "title": "string",
  "selftext": "string",
  "url": "string",
  "created_utc": "float",
  "now_time": "float",
  "subreddit": "string",
  "title_sentiment": [{"label": "string", "score": "float"}],
  "selftext_sentiment": [{"label": "string", "score": "float"}]
}
```

### DashboardData
```json
{
  "posts": [RedditPost],
  "total_count": "integer",
  "last_updated": "datetime",
  "sentiment_summary": {
    "positive": "integer",
    "negative": "integer",
    "neutral": "integer"
  }
}
```

## Usage Examples

### Get recent data for dashboard
```bash
curl "http://localhost:8000/recent-data?hours=6"
```

### Get sentiment summary for last 12 hours
```bash
curl "http://localhost:8000/sentiment-summary?hours=12"
```

### Get subreddit statistics for last 24 hours
```bash
curl "http://localhost:8000/subreddit-stats?hours=24"
```

## Dashboard Integration

The dashboard should poll these endpoints every few seconds for real-time updates:

1. **Primary endpoint**: `/recent-data` - Get latest posts and sentiment data
2. **Summary endpoint**: `/sentiment-summary` - Get overall statistics
3. **Subreddit endpoint**: `/subreddit-stats` - Get breakdown by subreddit

## Configuration

- **MongoDB URI**: `mongodb://mongo:27017` (default)
- **Database**: `redditPosts`
- **Collection**: `posts`
- **Port**: 8000

## Running the API

### With Docker Compose
```bash
docker-compose up sentiment-dashboard-api
```

### Standalone
```bash
cd api
pip install -e .
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Monitoring

The API includes Prometheus metrics for:
- Total data requests
- Error counts
- Response latency
- MongoDB connection status

Access metrics at `/metrics` endpoint.