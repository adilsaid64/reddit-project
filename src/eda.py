import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
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



def generate_word_cloud(df, text_column='cleaned_text'):
    text = ' '.join(df[text_column].astype(str).tolist())
    wordcloud = WordCloud(background_color='white', width=800, height=400).generate(text)

    buf = io.BytesIO()
    wordcloud.to_image().save(buf, format='PNG')
    buf.seek(0)
    wordcloud_url = base64.b64encode(buf.getvalue()).decode('utf8')

    return wordcloud_url