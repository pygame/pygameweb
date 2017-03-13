""" Really simple comment classifier to see if it's spam.

"""

_comment_pipeline = None
def classify_comment(comment):
    """Classify the comment.

    :param comment: should have a message attribute.
    """
    global _comment_pipeline
    from sklearn.externals import joblib

    model_is_not_loaded = _comment_pipeline is None
    if model_is_not_loaded:
        import pygameweb.comment.classifier_train
        import pygameweb.config
        model_fname = pygameweb.config.Config.COMMENT_MODEL
        _comment_pipeline = joblib.load(model_fname)

    return _comment_pipeline.predict([comment.message])[0]
