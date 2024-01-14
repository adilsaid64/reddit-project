import streamlit as st
import pandas as pd
from src.pipelines import top_posts_subreddit_pipeline, comments_pipeline
from src.logger_config import setup_logger
from src.eda import *

logger = setup_logger()

st.set_page_config(layout="wide")


def analyze_sentiment(df, post_id):
    return df[df['title']==post_id]


def main():
    st.title("Reddit Sentiment Analysis")

    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()
    if 'subreddit_name' not in st.session_state:
        st.session_state['subreddit_name'] = ''

    with st.sidebar:
        subreddit_name = st.text_input("Enter a subreddit:", st.session_state['subreddit_name'])
        post_limit = st.number_input("Number of top posts to fetch:", min_value=1, max_value=100, value=5, step=1)
        comment_limit = st.number_input("Limit of comments per post:", min_value=1, max_value=500, value=10, step=1)

    # GET data only if subreddit name changes or df is empty
    if subreddit_name and (subreddit_name != st.session_state['subreddit_name'] or st.session_state['df'].empty):
        with st.spinner('Fetching posts...'):
            st.session_state['df'] = top_posts_subreddit_pipeline(subreddit_name=subreddit_name, post_limit=post_limit, comment_limmit=comment_limit)
        st.session_state['subreddit_name'] = subreddit_name

    st.write("Subreddit Posts:")
    st.dataframe(st.session_state['df'])
    
    col1, col2= st.columns(2)
    with col1:
        st.header('Sentiment Distribution')

        st.plotly_chart(plot_sentiment_distribution_plotly(st.session_state['df'], 'sentiment_clean_title_label'))

    with col2:
        st.header('Word Count')
        st.plotly_chart(plot_word_count(st.session_state['df'], 'clean_title'))

    for index, row in st.session_state['df'].iterrows():
        with st.expander(f"Analyze Post: {index} - {row['title']}"):
                
            if st.button(f"Analyze", key=row['title']):
                with st.spinner(f"Analyzing post {row['title']}..."):
                    sentiment = analyze_sentiment(st.session_state['df'], row['title'])
                    logger.info(sentiment.index)
                    comment_df = comments_pipeline(sentiment, 'comments', 'body')
                    st.dataframe(comment_df)
                    col1, col2= st.columns(2)
                    with col1:
                        st.header('Sentiment Distribution')
        
                    with col2:
                        st.header('Word Count')
         
if __name__ == "__main__":
    main()
