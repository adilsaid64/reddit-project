from transformers import DistilBertTokenizer, TFDistilBertForSequenceClassification
from transformers import pipeline

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model = TFDistilBertForSequenceClassification.from_pretrained(model_name)
tokenizer = DistilBertTokenizer.from_pretrained(model_name)

nlp_pipeline = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)


def get_sentiment(df, text_col, nlp_pipeline = nlp_pipeline):
    '''
    Gets sentiment on a dataframe col
    
    :params df (pd.DataFrame) : The data in a pandas dataframe.
    :params text_col (str) : The column containing the text you want to get sentiment on.
    
    :returns df (pd.DataFrame) : The dataframe with a new column containing sentiment.
    '''
    df[f'sentiment_{text_col}'] = df[text_col].apply(lambda x: nlp_pipeline(x))
    return df