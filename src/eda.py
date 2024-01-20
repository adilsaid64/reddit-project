import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import io
import base64

import plotly.express as px
import plotly.graph_objs as go


def plot_sentiment_distribution_plotly(df, sentiment_column='sentiment'):
    sentiment_counts = df[sentiment_column].value_counts()
    fig = px.bar(sentiment_counts, 
                 x=sentiment_counts.index, 
                 y=sentiment_counts.values,
                 labels={'x': 'Sentiment', 'y': 'Frequency'},
                 title='Sentiment Distribution')
    return fig


def plot_sentiment_distribution(df, sentiment_column='sentiment'):
    plt.figure(figsize=(10, 6))
    sns.countplot(x=sentiment_column, data=df)
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')
    fig = plt.gcf()
    return fig

def text_summary(df, text_column='cleaned_text'):
    df['word_count'] = df[text_column].apply(lambda x: len(x.split()))
    text_summary_stats = df['word_count'].describe().to_frame().to_html()

    return text_summary_stats

def generate_word_cloud_based_on_sentiment(df, text_column='cleaned_text', sentiment_column = 'sentiment_clean_title_label', sentiment = None):
    if isinstance(sentiment, str):    
        if sentiment == 'pos':
            df = df[df[sentiment_column]=='POSITIVE']
        elif sentiment =='neg':
            df = df[df[sentiment_column]=='NEGATIVE']
        else:
            None
    else:
        None
    text = ' '.join(df[text_column].astype(str).tolist())
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate(text)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")

    return fig

# Need a pipeline to get data in certain order. Current pipeline gets the top posts from each subreddit. Need to be able to get the latest posts.
# Like get the latest 30 posts. This way we can see how sentiment has changed over time. Or get all posts from last 6 months or something.
def plot_sentiment_timeseries(df, sentiment_colum = 'sentiment_clean_title_label', time_column = 'timestamp'):
    df['year'] = df[time_column].dt.year
    df['month'] = df[time_column].dt.month
    df['day'] = df[time_column].dt.day

    result = df.groupby(['year', 'month', 'day'])[sentiment_colum].value_counts().unstack()

    data = result.reset_index()
    data['date'] = pd.to_datetime(data[['year', 'month', 'day']])

    # Create traces for positive and negative sentiments
    trace_positive = go.Scatter(x=data['date'], y=data['POSITIVE'], mode='lines+markers', name='Positive')
    trace_negative = go.Scatter(x=data['date'], y=data['NEGATIVE'], mode='lines+markers', name='Negative')
    fig = go.Figure(data=[trace_positive, trace_negative])
    fig.update_layout(title='Sentiment Analysis Over Time',
                    xaxis_title='Date',
                    yaxis_title='Count',
                    template='plotly_dark')
    return fig


def plot_word_count(df, text_column, n_words=15):
    all_words = df[text_column].str.split().explode()

    word_counts = all_words.value_counts().head(n_words)

    word_count_df = word_counts.reset_index()
    word_count_df.columns = ['word', 'count']

    fig = px.bar(word_count_df, x='count', y='word', orientation='h',
                 title=f'Top {n_words} Word Count',
                 labels={'count': 'Count', 'word': 'Word'})
    
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig
