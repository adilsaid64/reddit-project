import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import io
import base64

import plotly.express as px

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

    buf = io.BytesIO()
    wordcloud.to_image().save(buf, format='PNG')
    buf.seek(0)
    wordcloud_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return wordcloud_url

# Need a pipeline to get data in certain order. Current pipeline gets the top posts from each subreddit. Need to be able to get the latest posts.
# Like get the latest 30 posts. This way we can see how sentiment has changed over time. Or get all posts from last 6 months or something.
def plot_sentiment_timeseries(df, sentiment_colum = 'sentiment_clean_title_label', time_column = 'created_utc'):
    return

def plot_word_count_old(df, text_column, n_words = 15):
 
    df['word_list'] = df[text_column].str.split()
    results = Counter()
    df['counter'] = df['word_list'].apply(results.update)

    word_count_data = {'word' : list(results.keys()),
            'count' : list(results.values())}
    word_count_df = pd.DataFrame(word_count_data)

    plt.figure(figsize=(10, 6))
    sns.barplot(data = word_count_df.sort_values(by = 'count', ascending=False)[:n_words], y = 'word', x = 'count')
    plt.title(f'Top {n_words} Word Count')
    plt.xlabel('Count')
    plt.ylabel('Word')

    return



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
