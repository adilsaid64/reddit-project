# Reddit Sentiment Dashboard

A real-time Streamlit dashboard that displays sentiment analysis data from Reddit posts.

## Features

- **Real-time Data Polling** - Automatically refreshes every 5 seconds
- **Interactive Charts** - Sentiment distribution, timeline trends, and subreddit breakdowns
- **Configurable Time Ranges** - View data from 1 hour to 72 hours
- **Responsive Layout** - Wide layout with sidebar controls
- **Error Handling** - Graceful handling of API connection issues
- **Session State Management** - Persistent settings and data caching

## Dashboard Components

### Main Dashboard
- **Key Metrics** - Total posts, positive/negative/neutral counts
- **Sentiment Distribution** - Interactive pie chart
- **Sentiment Timeline** - Line chart showing trends over time
- **Recent Posts Table** - Detailed view with sentiment scores

### Sidebar Controls
- **Time Range Selection** - 1, 6, 12, 24, 48, or 72 hours
- **Auto-refresh Toggle** - Enable/disable automatic updates
- **Manual Refresh** - Force immediate data update
- **API Status** - Connection health indicator

### Summary Statistics
- **Overall Metrics** - Time range, total posts, unique subreddits
- **Subreddit Breakdown** - Bar chart and detailed statistics
- **Sentiment Distribution** - Per-subreddit sentiment analysis

## Data Sources

The dashboard polls these API endpoints:
- `/recent-data` - Main sentiment data
- `/sentiment-summary` - Aggregated statistics  
- `/subreddit-stats` - Subreddit breakdown

## Running the Dashboard

### With Docker Compose (Recommended)
```bash
docker-compose up streamlit-dashboard
```

### Standalone
```bash
cd streamlit-app
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

### Environment Variables
- `API_BASE_URL` - Base URL for the sentiment API (default: http://sentiment-dashboard-api:8000)

### Port Configuration
- **Dashboard**: Port 8501
- **API**: Port 8000
- **MongoDB**: Port 27017

## Development

### Dependencies
- `streamlit` - Web framework
- `requests` - HTTP client for API calls
- `pandas` - Data manipulation
- `plotly` - Interactive charts

### File Structure
```
streamlit-app/
├── app.py              # Main dashboard application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
└── README.md          # This file
```

## Best Practices Implemented

1. **Session State Management** - Persistent user preferences
2. **Error Handling** - Graceful API failure handling
3. **Caching** - Efficient data fetching and display
4. **Responsive Design** - Wide layout with proper column management
5. **Logging** - Comprehensive error logging
6. **Type Hints** - Python type annotations for better code quality
7. **Modular Functions** - Separated concerns for maintainability

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if sentiment-dashboard-api service is running
   - Verify API_BASE_URL environment variable
   - Check Docker network connectivity

2. **No Data Displayed**
   - Ensure MongoDB has data
   - Check API endpoints are responding
   - Verify time range selection

3. **Dashboard Not Loading**
   - Check Streamlit logs
   - Verify port 8501 is accessible
   - Check container health status

### Logs
View logs with:
```bash
docker-compose logs streamlit-dashboard
```

## Performance Notes

- **Auto-refresh**: Set to 5 seconds for real-time updates
- **Data Limits**: API returns max 100 posts per request
- **Caching**: Session state prevents unnecessary API calls
- **Charts**: Plotly charts are optimized for large datasets
