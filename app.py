from flask import Flask, render_template
import pandas as pd
from src.pipelines import top_posts_subreddit_pipeline

app = Flask(__name__)

@app.route('/')
def sentiment_dashboard():
    df = top_posts_subreddit_pipeline('Sudan', 10, 10)
    sentiment_counts = df['sentiment_clean_title_label'].value_counts()
    labels = sentiment_counts.index.tolist()
    values = sentiment_counts.values.tolist()
    return render_template('sentiment_dashboard.html', labels=labels, values=values)

if __name__ == '__main__':
    app.run(debug=True)
