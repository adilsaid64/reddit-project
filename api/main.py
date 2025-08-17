import time
import logging
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, Counter, Histogram
import uvicorn
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logger = logging.getLogger("uvicorn")

# MongoDB connection
MONGODB_URI = "mongodb://mongo:27017"
DB_NAME = "redditPosts"
COLLECTION_NAME = "posts"

# Metrics
DATA_REQUESTS = Counter("data_requests_total", "Total number of data requests")
DATA_ERRORS = Counter("data_errors_total", "Total number of failed data requests")
DATA_LATENCY = Histogram("data_latency_seconds", "Data retrieval latency in seconds")

# MongoDB client
mongo_client: Optional[MongoClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client
    try:
        mongo_client = MongoClient(MONGODB_URI)
        # Test connection
        mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        mongo_client = None
    
    yield
    
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")

app = FastAPI(
    title="Sentiment Dashboard API", 
    description="API for real-time sentiment dashboard data", 
    lifespan=lifespan
)

# Pydantic models
class SentimentData(BaseModel):
    label: str
    score: float

class RedditPost(BaseModel):
    id: str = Field(alias="_id")
    title: str
    selftext: str
    url: str
    created_utc: float
    now_time: float
    subreddit: str
    title_sentiment: list[SentimentData]
    selftext_sentiment: list[SentimentData]

class DashboardData(BaseModel):
    posts: list[RedditPost]
    total_count: int
    last_updated: datetime
    sentiment_summary: dict

class TimeRangeQuery(BaseModel):
    hours: int = Field(default=24, ge=1, le=168, description="Hours to look back (1-168)")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if mongo_client is None:
        raise HTTPException(status_code=503, detail="MongoDB not connected")
    return {"status": "healthy", "mongodb": "connected"}

@app.get("/recent-data", response_model=DashboardData)
async def get_recent_data(hours: int = 24):
    """Get recent sentiment data for the dashboard"""
    start_time = time.time()
    DATA_REQUESTS.inc()
    
    try:
        if mongo_client is None:
            raise HTTPException(status_code=503, detail="MongoDB not connected")
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time_range = end_time - timedelta(hours=hours)
        
        # Query MongoDB for recent posts
        collection = mongo_client[DB_NAME][COLLECTION_NAME]
        
        # Get posts from the last N hours
        query = {
            "now_time": {
                "$gte": start_time_range.timestamp(),
                "$lte": end_time.timestamp()
            }
        }
        
        # Sort by most recent first
        posts_cursor = collection.find(query).sort("now_time", -1).limit(100)
        
        posts = []
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        
        for post_doc in posts_cursor:
            # Convert MongoDB ObjectId to string
            post_doc["_id"] = str(post_doc["_id"])
            
            # Count sentiments
            if post_doc.get("title_sentiment"):
                for sentiment in post_doc["title_sentiment"]:
                    if sentiment.get("label") == "POSITIVE":
                        sentiment_counts["positive"] += 1
                    elif sentiment.get("label") == "NEGATIVE":
                        sentiment_counts["negative"] += 1
                    else:
                        sentiment_counts["neutral"] += 1
            
            posts.append(RedditPost(**post_doc))
        
        # Get total count for the time range
        total_count = collection.count_documents(query)
        
        dashboard_data = DashboardData(
            posts=posts,
            total_count=total_count,
            last_updated=end_time,
            sentiment_summary=sentiment_counts
        )
        
        return dashboard_data
        
    except Exception as e:
        DATA_ERRORS.inc()
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    finally:
        latency = time.time() - start_time
        DATA_LATENCY.observe(latency)

@app.get("/sentiment-summary")
async def get_sentiment_summary(hours: int = 24):
    """Get sentiment summary statistics"""
    try:
        if mongo_client is None:
            raise HTTPException(status_code=503, detail="MongoDB not connected")
        
        collection = mongo_client[DB_NAME][COLLECTION_NAME]
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time_range = end_time - timedelta(hours=hours)
        
        # Aggregate sentiment data
        pipeline = [
            {
                "$match": {
                    "now_time": {
                        "$gte": start_time_range.timestamp(),
                        "$lte": end_time.timestamp()
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_posts": {"$sum": 1},
                    "total_subreddits": {"$addToSet": "$subreddit"}
                }
            }
        ]
        
        result = list(collection.aggregate(pipeline))
        
        if result:
            summary = result[0]
            return {
                "time_range_hours": hours,
                "total_posts": summary["total_posts"],
                "unique_subreddits": len(summary["total_subreddits"]),
                "last_updated": end_time.isoformat()
            }
        else:
            return {
                "time_range_hours": hours,
                "total_posts": 0,
                "unique_subreddits": 0,
                "last_updated": end_time.isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error fetching sentiment summary: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/subreddit-stats")
async def get_subreddit_stats(hours: int = 24):
    """Get statistics grouped by subreddit"""
    try:
        if mongo_client is None:
            raise HTTPException(status_code=503, detail="MongoDB not connected")
        
        collection = mongo_client[DB_NAME][COLLECTION_NAME]
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time_range = end_time - timedelta(hours=hours)
        
        # Aggregate by subreddit
        pipeline = [
            {
                "$match": {
                    "now_time": {
                        "$gte": start_time_range.timestamp(),
                        "$lte": end_time.timestamp()
                    }
                }
            },
            {
                "$group": {
                    "_id": "$subreddit",
                    "post_count": {"$sum": 1},
                    "sentiment_breakdown": {
                        "$push": {
                            "title_sentiment": "$title_sentiment",
                            "selftext_sentiment": "$selftext_sentiment"
                        }
                    }
                }
            },
            {
                "$sort": {"post_count": -1}
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        subreddit_stats = []
        for result in results:
            # Calculate sentiment distribution for this subreddit
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for sentiment_data in result["sentiment_breakdown"]:
                if sentiment_data.get("title_sentiment"):
                    for sentiment in sentiment_data["title_sentiment"]:
                        if sentiment.get("label") == "POSITIVE":
                            positive_count += 1
                        elif sentiment.get("label") == "NEGATIVE":
                            negative_count += 1
                        else:
                            neutral_count += 1
                
                if sentiment_data.get("selftext_sentiment"):
                    for sentiment in sentiment_data["selftext_sentiment"]:
                        if sentiment.get("label") == "POSITIVE":
                            positive_count += 1
                        elif sentiment.get("label") == "NEGATIVE":
                            negative_count += 1
                        else:
                            neutral_count += 1
            
            subreddit_stats.append({
                "subreddit": result["_id"],
                "post_count": result["post_count"],
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                }
            })
        
        return {
            "time_range_hours": hours,
            "subreddits": subreddit_stats,
            "last_updated": end_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching subreddit stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
