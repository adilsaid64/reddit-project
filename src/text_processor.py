import re
import string
import nltk
import contractions
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

def lemmatize_text(text):
    '''
    Lemmatize text

    Example:
    >>> lemmatize_text('change changing changes changed changer')
    change change change change change
    '''
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text)
    return ' '.join([lemmatizer.lemmatize(word) for word in tokens])

def clean_text(text):
    '''
    Apply all cleaning functions to text
    '''
    logger.info('expand_contractions')
    text = expand_contractions(text)
    logger.info('lowercase_text')
    text = lowercase_text(text)
    logger.info('remove_special_characters')
    text = remove_special_characters(text)
    logger.info('remove_punctuation')
    text = remove_punctuation(text)
    logger.info('remove_numbers')
    text = remove_numbers(text)
    logger.info('remove_whitespace')
    text = remove_whitespace(text)
    logger.info('remove_stopwords')
    text = remove_stopwords(text)
    logger.info('lemmatize_text')
    text = lemmatize_text(text)
    logger.info('Done')
    return text