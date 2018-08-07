""" For commenting on things.
"""

from flask import (Blueprint, render_template, abort, redirect, flash, url_for)
from flask_sqlalchemy_session import current_session
from flask_security import login_required, roles_required

from pygameweb.comment.models import CommentPost

comment_blueprint = Blueprint('comment',
                              __name__,
                              template_folder='../templates/',
                              static_folder='static')


def comments_for(forum):
    """ the forum.
    """
    is_spam, is_deleted = False, False
    posts = (current_session
             .query(CommentPost)
             .order_by(CommentPost.created_at.desc())
             .filter(CommentPost.is_spam == is_spam)
             .filter(CommentPost.is_deleted == is_deleted)
             .limit(40)
             .all())
    return posts



@comment_blueprint.route('/comment/jquery.plugin.docscomments.js', methods=['GET'])
def comments_js():
    """ for including in document pages.
    """
    return comment_blueprint.send_static_file('jquery.plugin.docscomments.js')


@comment_blueprint.route('/comments/<forum>',
                         methods=['GET'])
def recent_comments(forum):
    """ shows recent comments.
    """
    return render_template('comment/recent.html',
                           comments_for=comments_for,
                           forum=forum)


@comment_blueprint.route('/comment/<int:comment_post_id>/<action>',
                         methods=['POST'])
@login_required
@roles_required('moderator')
def mark_comment(comment_post_id, action):
    """ with comment_post_id as deleted or spam.
    """
    comment = (current_session
               .query(CommentPost)
               .filter(CommentPost.id == comment_post_id)
               .first())
    if not comment:
        abort(404)
    if action == 'delete':
        comment.is_deleted = True
        flash('Comment marked deleted.')
    elif action == 'spam':
        comment.is_spam = True
        flash('Comment marked spam.')
    else:
        abort(404)

    current_session.add(comment)
    current_session.commit()

    return redirect('/')


def add_comment(app):
    """ to the app.
    """
    app.register_blueprint(comment_blueprint)
