"""For training the comment spam classifier.
"""

import os

import numpy
from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.externals import joblib

from pygameweb.db import _get_session
from pygameweb.comment.models import CommentPost

def get_comment_data():
    trans, session = _get_session()
    spam = session.query(CommentPost).filter(CommentPost.is_spam == True).all()
    ham = session.query(CommentPost).filter(CommentPost.is_spam != True).all()
    return [(spam, 'spam'), (ham, 'ham')]

def build_df(comments, classification):
    """Creates a dataframe from the comments.

    :param classification: either 'spam', or 'ham'.
    """
    rows = []
    index = []
    for comment in comments:
        rows.append({'text': comment.message, 'class': classification})
        index.append(comment.id)
    return DataFrame(rows, index=index)

def process_comment_data(comment_data):
    data = DataFrame({'text': [], 'class': []})
    for comments, classification in comment_data:
        built_data = build_df(comments, classification)
        data = data.append(built_data)
    return data

def make_classifier():
    pipeline = Pipeline([
        ('count_vectorizer',   CountVectorizer(ngram_range=(1, 2))),
        ('classifier',         MultinomialNB())
    ])
    return pipeline

def test_run_train(pipeline, data):
    """We train, and cross validate to see how well we are going.
    """
    ham_scores = []
    spam_scores = []

    # http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html
    confusion = numpy.array([[0, 0], [0, 0]])
    for train_indices, test_indices in KFold(n_splits=12, shuffle=True).split(data):
        train_text = data.iloc[train_indices]['text'].values
        train_y = data.iloc[train_indices]['class'].values.astype(str)

        test_text = data.iloc[test_indices]['text'].values
        test_y = data.iloc[test_indices]['class'].values.astype(str)

        pipeline.fit(train_text, train_y)
        predictions = pipeline.predict(test_text)

        confusion += confusion_matrix(test_y, predictions)
        ham_score = f1_score(test_y, predictions, pos_label='ham')
        ham_scores.append(ham_score)
        spam_score = f1_score(test_y, predictions, pos_label='spam')
        spam_scores.append(spam_score)

    print(f'num comments:{len(data)}')
    print(f'ham_score:{sum(ham_scores)/len(ham_scores)}', )
    print(f'spam_score:{sum(spam_scores)/len(spam_scores)}', )
    print(confusion)

def train_full(pipeline, data, output_fname):
    """We train using all the data we have.
    """
    train_text = data['text'].values
    train_y = data['class'].values.astype(str)
    pipeline.fit(train_text, train_y)
    joblib.dump(pipeline, output_fname, compress=9)


def train_comments(output_fname, test_run):
    """ Trains the spam classifier on our comment data.

    :param output_fname: is where the model is saved.
    :param test_run: use a test set.
    """

    pipeline = make_classifier()
    comment_data = get_comment_data()
    data = process_comment_data(comment_data)

    # import pdb;pdb.set_trace()
    if test_run:
        test_run_train(pipeline, data)
    else:
        train_full(pipeline, data, output_fname)


def classify_comments():
    """Classify comments into ham/spam and save the model.
    """
    import pygameweb.config
    model_fname = pygameweb.config.Config.COMMENT_MODEL
    train_comments(model_fname, test_run=0)
