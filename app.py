from flask import Flask
from flask import request
from flask import render_template

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag

from joblib import load
import re, string

app = Flask(__name__)

# Your home route. Does not allow POST requests.
@app.route('/')
def home():

    return render_template('index.html') # return the html file under templates folder

# Home route that does allow POST requests.
@app.route('/',methods=['POST'])
def analyze():

    # this dataset is required for analysis
    punkt_downloaded = False

    if punkt_downloaded == False:
        nltk.download('punkt')

    tweet = request.form.get('text') # get the text from the html form that was submitted. 
    
    # clean the tweet and return tokens. This is from previous work.
    def remove_noise(tweet_tokens, stop_words = ()):

        cleaned_tokens = []

        for token, tag in pos_tag(tweet_tokens):
            token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                        '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
            token = re.sub("(@[A-Za-z0-9_]+)","", token)

            if tag.startswith("NN"):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)

            if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())
        return cleaned_tokens

    # load the saved classifier
    clf = load('tweet_classifier.joblib')

    custom_tweet = tweet
    
    # prep tweet for sentiment analysis
    custom_tokens = remove_noise(word_tokenize(custom_tweet))

    sentiment = clf.classify(dict([token, True] for token in custom_tokens))

    # your brows may render this differently if you remove str()
    result = str({'tweet':tweet,
              'sentiment': sentiment})
              
    return render_template('index.html',tweet = tweet, sentiment = sentiment)


if __name__== '__main__':

    app.run(debug=True)