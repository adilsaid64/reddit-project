import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Reddit Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://sentiment-dashboard-api:8000"
POLLING_INTERVAL = 5

if "last_poll" not in st.session_state:
    st.session_state.last_poll = None
if "data" not in st.session_state:
    st.session_state.data = None
if "error" not in st.session_state:
    st.session_state.error = None
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "posts_df" not in st.session_state:
    st.session_state.posts_df = None
if "subreddit_stats" not in st.session_state:
    st.session_state.subreddit_stats = None
if "sentiment_summary" not in st.session_state:
    st.session_state.sentiment_summary = None
if "timeline_data" not in st.session_state:
    st.session_state.timeline_data = None
if "cumulative_data" not in st.session_state:
    st.session_state.cumulative_data = None
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

def fetch_api_data(endpoint: str, params: Optional[dict[str, Any]] = None) -> Optional[dict[str, Any]]:
    """Fetch data from API endpoint with error handling."""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        st.session_state.error = f"Failed to fetch data: {str(e)}"
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.session_state.error = f"Unexpected error: {str(e)}"
        return None

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def create_sentiment_bar_chart(sentiment_data: dict[str, int]) -> go.Figure:
    """Create a bar chart for sentiment distribution."""
    if not sentiment_data or sum(sentiment_data.values()) == 0:
        return go.Figure()
    
    sentiments = list(sentiment_data.keys())
    counts = list(sentiment_data.values())
    
    fig = go.Figure(data=[
        go.Bar(
            x=sentiments,
            y=counts,
            marker_color=['#00ff00', '#ff0000', '#808080'],
            text=counts,
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Sentiment Distribution",
        xaxis_title="Sentiment",
        yaxis_title="Count",
        showlegend=False,
        height=400
    )
    
    return fig

def create_subreddit_bar_chart(subreddit_data: list) -> go.Figure:
    """Create a bar chart for subreddit post counts."""
    if not subreddit_data:
        return go.Figure()
    
    df = pd.DataFrame(subreddit_data)
    fig = px.bar(
        df,
        x="subreddit",
        y="post_count",
        title="Posts by Subreddit",
        color="post_count",
        color_continuous_scale="viridis"
    )
    fig.update_xaxes(tickangle=45)
    return fig

def create_sentiment_timeline(posts: list) -> go.Figure:
    """Create a time series chart showing sentiment trends over time."""
    if not posts:
        return go.Figure()
    
    try:
        timeline_data = []
        for post in posts:
            timestamp = datetime.fromtimestamp(post.get("now_time", 0))
            
            if post.get("title_sentiment"):
                for sentiment in post["title_sentiment"]:
                    timeline_data.append({
                        "timestamp": timestamp,
                        "sentiment": sentiment.get("label", "NEUTRAL"),
                        "score": sentiment.get("score", 0)
                    })
            
            if post.get("selftext_sentiment"):
                for sentiment in post["selftext_sentiment"]:
                    timeline_data.append({
                        "timestamp": timestamp,
                        "sentiment": sentiment.get("label", "NEUTRAL"),
                        "score": sentiment.get("score", 0)
                    })
        
        if not timeline_data:
            st.info("No sentiment data available for timeline")
            return go.Figure()
        
        df = pd.DataFrame(timeline_data)
        
        if len(df) > 100:
            df["time_bucket"] = df["timestamp"].dt.floor("30S")
        elif len(df) > 50:
            df["time_bucket"] = df["timestamp"].dt.floor("1T")
        else:
            df["time_bucket"] = df["timestamp"].dt.floor("5T")
        
        time_sentiment = df.groupby(["time_bucket", "sentiment"]).size().reset_index(name="count")
        pivot_data = time_sentiment.pivot(index="time_bucket", columns="sentiment", values="count").fillna(0)
        
        fig = go.Figure()
        colors = {"POSITIVE": "#00ff00", "NEGATIVE": "#ff0000", "NEUTRAL": "#808080"}
        
        for sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            if sentiment in pivot_data.columns:
                fig.add_trace(go.Scatter(
                    x=pivot_data.index,
                    y=pivot_data[sentiment],
                    mode="lines+markers",
                    name=sentiment,
                    line=dict(width=2, color=colors.get(sentiment, "#000000")),
                    marker=dict(size=4, color=colors.get(sentiment, "#000000")),
                    hovertemplate=f"<b>{sentiment}</b><br>" +
                                "Time: %{x}<br>" +
                                "Count: %{y}<br>" +
                                "<extra></extra>"
                ))
        
        fig.update_layout(
            title="Real-time Sentiment Trends (Dynamic Time Buckets)",
            xaxis_title="Time",
            yaxis_title="Sentiment Count",
            height=400,
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            tickformat="%H:%M:%S",
            tickmode="auto",
            nticks=10,
            tickangle=45
        )
        
        fig.update_yaxes(rangemode="tozero")
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating timeline chart: {str(e)}")
        logger.error(f"Timeline chart error: {e}")
        return go.Figure()

def create_cumulative_sentiment_timeline(posts: list) -> go.Figure:
    """Create a cumulative time series chart showing running sentiment totals over time."""
    if not posts:
        return go.Figure()
    
    try:
        timeline_data = []
        for post in posts:
            timestamp = datetime.fromtimestamp(post.get("now_time", 0))
            
            if post.get("title_sentiment"):
                for sentiment in post["title_sentiment"]:
                    timeline_data.append({
                        "timestamp": timestamp,
                        "sentiment": sentiment.get("label", "NEUTRAL"),
                        "score": sentiment.get("score", 0)
                    })
            
            if post.get("selftext_sentiment"):
                for sentiment in post["selftext_sentiment"]:
                    timeline_data.append({
                        "timestamp": timestamp,
                        "sentiment": sentiment.get("label", "NEUTRAL"),
                        "score": sentiment.get("score", 0)
                    })
        
        if not timeline_data:
            st.info("No sentiment data available for cumulative timeline")
            return go.Figure()
        
        df = pd.DataFrame(timeline_data)
        df = df.sort_values("timestamp")
        
        if len(df) > 100:
            df["time_bucket"] = df["timestamp"].dt.floor("30S")
        elif len(df) > 50:
            df["time_bucket"] = df["timestamp"].dt.floor("1T")
        else:
            df["time_bucket"] = df["timestamp"].dt.floor("5T")
        
        time_sentiment = df.groupby(["time_bucket", "sentiment"]).size().reset_index(name="count")
        pivot_data = time_sentiment.pivot(index="time_bucket", columns="sentiment", values="count").fillna(0)
        cumulative_data = pivot_data.cumsum()
        
        fig = go.Figure()
        colors = {"POSITIVE": "#00ff00", "NEGATIVE": "#ff0000", "NEUTRAL": "#808080"}
        
        for sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]:
            if sentiment in cumulative_data.columns:
                fig.add_trace(go.Scatter(
                    x=cumulative_data.index,
                    y=cumulative_data[sentiment],
                    mode="lines+markers",
                    name=f"{sentiment} (Cumulative)",
                    line=dict(width=3, color=colors.get(sentiment, "#000000")),
                    marker=dict(size=5, color=colors.get(sentiment, "#000000")),
                    hovertemplate=f"<b>{sentiment}</b><br>" +
                                "Time: %{x}<br>" +
                                "Cumulative Count: %{y}<br>" +
                                "<extra></extra>",
                    fill="tonexty" if sentiment == "POSITIVE" else None
                ))
        
        fig.update_layout(
            title="Cumulative Sentiment Trends Over Time",
            xaxis_title="Time",
            yaxis_title="Cumulative Sentiment Count",
            height=400,
            hovermode="x unified",
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        fig.update_xaxes(
            tickformat="%H:%M:%S",
            tickmode="auto",
            nticks=10,
            tickangle=45
        )
        
        fig.update_yaxes(rangemode="tozero")
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating cumulative timeline chart: {str(e)}")
        logger.error(f"Cumulative timeline chart error: {e}")
        return go.Figure()

def display_posts_table(posts: list) -> pd.DataFrame:
    """Display posts in a formatted table and return processed DataFrame."""
    if not posts:
        st.info("No posts available for the selected time range.")
        return pd.DataFrame()
    
    display_data = []
    for post in posts:
        primary_sentiment = "N/A"
        sentiment_score = 0.0
        if post.get("title_sentiment"):
            primary_sentiment = post["title_sentiment"][0].get("label", "N/A")
            sentiment_score = post["title_sentiment"][0].get("score", 0.0)
        
        title = post.get("title", "N/A")
        if len(title) > 50:
            title = title[:50] + "..."
        
        created_timestamp = post.get("created_utc", 0)
        created_date = datetime.fromtimestamp(created_timestamp)
        created_formatted = created_date.strftime("%Y-%m-%d %H:%M:%S")
        
        display_data.append({
            "Title": title,
            "Subreddit": post.get("subreddit", "N/A"),
            "Sentiment": primary_sentiment,
            "Score": f"{sentiment_score:.2f}",
            "Created": created_formatted,
            "URL": post.get("url", "N/A")
        })
    
    df = pd.DataFrame(display_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn("URL", max_chars=50),
            "Title": st.column_config.TextColumn("Title", width="medium"),
            "Sentiment": st.column_config.SelectboxColumn(
                "Sentiment",
                options=["POSITIVE", "NEGATIVE", "NEUTRAL"],
                default="NEUTRAL"
            )
        }
    )
    
    return df

def main():
    """Main dashboard function."""
    st.title("📊 Reddit Sentiment Analysis Dashboard")
    st.markdown("Real-time sentiment analysis of Reddit posts")
    
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        time_range = st.selectbox(
            "Time Range",
            options=[1, 6, 12, 24, 48, 72],
            format_func=lambda x: f"{x} hour{'s' if x > 1 else ''}",
            index=3
        )
        
        if "current_time_range" not in st.session_state:
            st.session_state.current_time_range = time_range
        elif st.session_state.current_time_range != time_range:
            st.session_state.current_time_range = time_range
            st.session_state.subreddit_stats = None
            st.session_state.posts_df = None
            st.session_state.sentiment_summary = None
            st.session_state.timeline_data = None
            st.session_state.cumulative_data = None
        
        auto_refresh = st.checkbox("Auto-refresh", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto_refresh
        
        if auto_refresh:
            st.info(f"Refreshing every {POLLING_INTERVAL} seconds")
        
        if st.button("🔄 Refresh Now", use_container_width=True):
            st.session_state.last_poll = None
            st.rerun()
        
        st.header("📡 API Status")
        if st.session_state.error:
            st.error("❌ API Error")
            st.error(st.session_state.error)
        else:
            st.success("✅ API Connected")
        
        if st.session_state.last_poll:
            st.info(f"Last updated: {st.session_state.last_poll.strftime('%H:%M:%S')}")
        
        debug_mode = st.checkbox("🐛 Show Debug Info", value=st.session_state.debug_mode)
        st.session_state.debug_mode = debug_mode
        
        if debug_mode:
            st.header("Debug Info")
            st.write("Session State Keys:", list(st.session_state.keys()))
            st.write("Posts DataFrame Shape:", 
                    st.session_state.posts_df.shape if st.session_state.posts_df is not None else "None")
            st.write("Current Time Range:", st.session_state.get("current_time_range", "Not set"))
            st.write("Sentiment Summary:", st.session_state.sentiment_summary)
            st.write("Timeline Data Available:", st.session_state.timeline_data is not None)
            st.write("Cumulative Data Available:", st.session_state.cumulative_data is not None)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📈 Real-time Sentiment Data")
        
        if (st.session_state.auto_refresh and 
            (st.session_state.last_poll is None or 
             datetime.now() - st.session_state.last_poll > timedelta(seconds=POLLING_INTERVAL))):
            
            with st.spinner("Fetching latest data..."):
                data = fetch_api_data("/recent-data", {"hours": time_range})
                if data:
                    st.session_state.data = data
                    st.session_state.last_poll = datetime.now()
                    st.session_state.error = None
        
        if st.session_state.data:
            data = st.session_state.data
            
            # Store sentiment summary in session state
            sentiment_summary = data.get("sentiment_summary", {})
            st.session_state.sentiment_summary = sentiment_summary
            
            col1_1, col1_2, col1_3, col1_4 = st.columns(4)
            with col1_1:
                st.metric("Total Posts", data.get("total_count", 0))
            with col1_2:
                st.metric("Positive", sentiment_summary.get("positive", 0))
            with col1_3:
                st.metric("Negative", sentiment_summary.get("negative", 0))
            with col1_4:
                st.metric("Neutral", sentiment_summary.get("neutral", 0))
            
            st.subheader("Sentiment Distribution")
            fig = create_sentiment_bar_chart(sentiment_summary)
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Sentiment Timeline")
            fig = create_sentiment_timeline(data.get("posts", []))
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Cumulative Sentiment Trends")
            fig_cumulative = create_cumulative_sentiment_timeline(data.get("posts", []))
            st.plotly_chart(fig_cumulative, use_container_width=True)
            
            st.subheader("Recent Posts")
            posts_df = display_posts_table(data.get("posts", []))
            st.session_state.posts_df = posts_df
            
        else:
            st.info("No data available. Check API connection and try refreshing.")
    
    with col2:
        st.header("🏷️ Subreddit Breakdown")
        
        if (st.session_state.subreddit_stats is None or 
            st.session_state.data is None):
            subreddit_data = fetch_api_data("/subreddit-stats", {"hours": time_range})
            if subreddit_data:
                st.session_state.subreddit_stats = subreddit_data
        else:
            subreddit_data = st.session_state.subreddit_stats
        
        if subreddit_data:
            fig = create_subreddit_bar_chart(subreddit_data.get("subreddits", []))
            st.plotly_chart(fig, use_container_width=True)
            
            for subreddit in subreddit_data.get("subreddits", [])[:5]:
                with st.expander(f"r/{subreddit['subreddit']} - {subreddit['post_count']} posts"):
                    sentiment_dist = subreddit.get("sentiment_distribution", {})
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Positive", sentiment_dist.get("positive", 0))
                    with col2:
                        st.metric("Negative", sentiment_dist.get("negative", 0))
                    with col3:
                        st.metric("Neutral", sentiment_dist.get("neutral", 0))
    
    st.markdown("---")
    st.markdown(
        "Dashboard updates automatically every 5 seconds. "
        "Use the sidebar controls to adjust time ranges and refresh settings."
    )
    
    if st.session_state.auto_refresh:
        time.sleep(POLLING_INTERVAL)
        st.rerun()

if __name__ == "__main__":
    main()
