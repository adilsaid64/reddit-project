import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud
from collections import Counter
import io
import base64

def plot_sentiment_distribution(df, sentiment_column='sentiment'):
    plt.figure(figsize=(10, 6))
    sns.countplot(x=sentiment_column, data=df)
    plt.title('Sentiment Distribution')
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return plot_url

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

def plot_word_count(df, text_column, n_words = 15):
 
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

    buf = io.BytesIO()
    plt.savefig(buf, format = 'png')
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return plot_url

