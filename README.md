# reddit-project

# Project Summary

This Reddit Sentiment Analysis Project introduces a powerful tool for real-time sentiment tracking on Reddit. Leveraging Streamlit for a seamless user interface, this project offers an intuitive platform for users to select any subreddit and generate a comprehensive sentiment dashboard. This dashboard not only captures the overall mood of the subreddit but also drills down into individual posts for more granular insights.

## User Experience

Users start by searching for a specific subreddit. The tool then processes recent posts and discussions, utilizing advanced sentiment analysis techniques to gauge the prevailing emotional tone - be it positive or negative. Furthermore, users can select individual posts to explore a detailed sentiment breakdown, enriching their understanding of the community's reactions and opinions.


## Applications
Sentiment analysis has many applications, here are some:

1. Event Reaction Analysis: For instance, in the world of sports, fans and analysts can gauge the reaction of a subreddit to events like Manchester United’s match outcomes. This tool helps in understanding the mood swings, trending discussions, and dominant opinions within fan communities.

2. Market Research and Business Intelligence: Companies can analyze customer feedback, reviews, and social media conversations to gauge public sentiment towards their products or services. This understanding helps in identifying areas of strength and aspects needing improvement. It allows for real-time monitoring of brand reputation. By analyzing the tone and emotions expressed in online discussions, companies can quickly respond to negative sentiments or capitalize on positive trends.

3. Personal Interest and Curiosity:

## What I have Learned
Working on this Reddit Sentiment Analysis project has equipped me with an understanding of sentiment analysis techniques and tools. These skills are directly transferable to business contexts, where I can effectively analyze customer feedback and market trends to provide actionable insights that drive strategic decisions and enhance customer engagement.

# Screenshots

![Alt text](ezgif.com-animated-gif-maker.gif)

# Data Pipeline and Storage

Data is fetched using `praw`.

Post data structure design:
```python
comments = []
comment_data = {
    'body': comment.body,
    'author': str(comment.author),
    'score': comment.score,
    'created_utc': comment.created_utc,
    'is_top_level': comment.is_root,
    'parent_id': comment.parent_id,
    'depth': comment.depth,
    'gilded': comment.gilded
    }
comments.append(comment_data)

post_data = {
    'title': post.title,
    'selftext': post.selftext,
    'score': post.score,
    'url': post.url,
    'author': str(post.author),
    'created_utc': post.created_utc,
    'num_comments': post.num_comments,
    'upvote_ratio': post.upvote_ratio,
    'subreddit': str(post.subreddit),
    'comments': comments
}
```

Data is then stored to an S3 Bucket using boto3 and sorted by subreddit.  

# Text Preprocessing 

Text preprocessing is a critical step in NLP (Natural Language Processing). It involves transforming raw text into a more analyzable and uniform format. This process is crucial for improving the performance of machine learning models and to understand the data better.

This section covers the text preprocesssing steps taken for this project. 

## Libaries Used:

- `re`: For regular expression operations.
- `string`: For string manipulation tasks.
- `nltk`:  Ued for a  of text processing tasks like tokenization and stopwords removal.
- `contractions`: Used to handle the expansion of contractions in English text.
- `emoji`: For converting emojis into text.
- `spacy`: Used here for lemmatization.


## 1. Expand Contractions
- **Function**: `expand_contractions`
- **Purpose**: Converts contractions (e.g., "can't", "won't") to their expanded forms (e.g., "cannot", "will not").
- **Why**: This standardizes text and aids in accurate word tokenization and analysis.

## 2. Replace Emoji
- **Function**: `replace_emoji`
- **Purpose**: Transforms emojis into corresponding text descriptions.
- **Why**: People use Emojis all the time and it would be a shame to not make use of them. This function enables the processing of emotional content represented by emojis, which is otherwise lost in text-only analysis.

## 3. Lowercase Text
- **Function**: `lowercase_text`
- **Purpose**: Converts all text to lowercase.
- **Why**: Ensures uniformity in text, removing case sensitivity from the analysis.

## 4. Removing Punctuation
- **Function**: `remove_punctuation`
- **Purpose**: Eliminates punctuation marks from the text.
- **Why**: Simplifies the text and removes unnecessary characters that might skew word frequencies or tokenization.

## 7. Remove Numbers
- **Function**: `remove_numbers`
- **Purpose**: Strips away all numeric characters.
- **Why**: Focuses analysis on textual content, especially when numbers are irrelevant to the context.

## 7. Remove Whitespace

- **Function**: `remove_whitespace`
- **Purpose**: Trims leading, trailing, and extra spaces within the text.
- **Why**: Standardizes spacing in text for consistent processing.

## 8. Remove Stopwords

- **Function**: `remove_stopwords`
- **Purpose**: Excludes common words (like "the", "is", "in") that offer little value in understanding the text's meaning.
- **Why**: Reduces the dataset size and focuses on more significant words for analysis.

## 9. Lemmatize Text

- **Function**: `lemmatize_text_spacy`
- **Purpose**: Converts words to their base or root form, considering the context.
- **Why**: Provides a more accurate and meaningful representation of words for analysis.

# EDA

# Machine Learning Model

# Limitations and Improvements