from flask import Flask, render_template, request, jsonify
import pandas as pd
from src.pipelines import top_posts_subreddit_pipeline
from src.eda import plot_sentiment_distribution, text_summary, generate_word_cloud_based_on_sentiment, plot_word_count
from src.logger_config import setup_logger

logger = setup_logger()
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subreddit = request.form['subreddit']
        no_posts = request.form['no_posts']
        
        df = top_posts_subreddit_pipeline(subreddit_name=subreddit, post_limit=int(no_posts), comment_limmit=5)

        sentiment_plot = plot_sentiment_distribution(df, sentiment_column='sentiment_clean_title_label')
        text_summary_stats = text_summary(df, text_column='clean_title')
        wordcloud_pos_url = generate_word_cloud_based_on_sentiment(df, text_column='clean_title', sentiment='pos')
        wordcloud_neg_url = generate_word_cloud_based_on_sentiment(df, text_column='clean_title', sentiment='neg')
        word_count_plot = plot_word_count(df, text_column='clean_title', n_words=15)
        # top positive words and top negative words?
        return render_template('index.html', 
                               tables=[df.to_html(classes='data')],
                               titles=df.columns.values, 
                               df = df,
                               sentiment_plot=sentiment_plot,
                               text_summary=text_summary_stats,
                               wordcloud_pos_url=wordcloud_pos_url,
                               wordcloud_neg_url = wordcloud_neg_url,
                               word_count_plot = word_count_plot)
    else:
        return render_template('index.html')

@app.route('/process-row/<int:index>', methods=['GET', 'POST'])
def process_row(index):
    if request.method == 'POST':
        row_data = request.json
        logger.info(row_data)
        return jsonify({"status": "success", "data": row_data})

if __name__ == '__main__':
    app.run(debug=True)
