from flask import Flask, render_template, request
import pandas as pd
from src.pipelines import top_posts_subreddit_pipeline
from src.eda import plot_sentiment_distribution, text_summary, generate_word_cloud
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subreddit = request.form['subreddit']

        df = top_posts_subreddit_pipeline(subreddit_name=subreddit, post_limit=5, comment_limmit=5)

        sentiment_plot = plot_sentiment_distribution(df, sentiment_column='sentiment_clean_title_label')
        text_summary_stats = text_summary(df, text_column='clean_title')
        wordcloud_url = generate_word_cloud(df, text_column='clean_title')

        return render_template('index.html', 
                               tables=[df.to_html(classes='data')],
                               titles=df.columns.values, 
                               sentiment_plot=sentiment_plot,
                               text_summary=text_summary_stats,
                               wordcloud_url=wordcloud_url)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
