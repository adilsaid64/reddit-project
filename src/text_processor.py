import re
import string
import nltk
import contractions
import emoji
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from .logger_config import setup_logger

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

logger = setup_logger()

def expand_contractions(text):
    '''
    Expands contractions in text to full form.

    Example: 
    >>> expand_contractions("I can't do this")
        "I cannot do this"
    '''
    return contractions.fix(text)

def replace_emoji(text):
    '''
    Replace Emoji in text with corresponding text description
    '''
    return emoji.demojize(text).replace("_", " ").replace(":", " ")

def lowercase_text(text):
    '''
    Convert text to lowercase.
    '''
    return text.lower()

def remove_punctuation(text):
    '''
    Remove punctuation from text.
    '''
    return text.translate(str.maketrans('', '', string.punctuation))

def remove_numbers(text):
    '''
    Remove numbers from text.
    '''
    return re.sub(r'\d+', '', text)

def remove_special_characters(text):
    '''
    Remove special characters from text
    '''
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

def remove_whitespace(text):
    '''
    Remove extra whitespaces from text
    '''
    return text.strip()

def remove_stopwords(text):
    '''
    Remove stopwords from text
    '''
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    return ' '.join([word for word in tokens if word not in stop_words])

def lemmatize_text(text): # Needs to use POS tagging
    '''
    Considers the context and conerts the words to its meaningfull base form.
    '''
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    return ' '.join([lemmatizer.lemmatize(word) for word in tokens])

def clean_text(text):
    '''
    Apply all cleaning functions to text
    '''
    logger.info(f'expand_contractions: {text}')
    text = expand_contractions(text)
    logger.info(f'replace_emoji: {text}')
    text = replace_emoji(text)
    logger.info(f'lowercase_text: {text}')
    text = lowercase_text(text)
    logger.info(f'remove_special_characters: {text}')
    text = remove_special_characters(text)
    logger.info(f'remove_punctuation: {text}')
    text = remove_punctuation(text)
    logger.info(f'remove_numbers: {text}')
    text = remove_numbers(text)
    logger.info(f'remove_whitespace: {text}')
    text = remove_whitespace(text)
    logger.info(f'remove_stopwords: {text}')
    text = remove_stopwords(text)
    logger.info(f'lemmatize_text: {text}')
    text = lemmatize_text(text)
    logger.info(f'Done: {text}')
    return text