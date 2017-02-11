from flask import Blueprint, render_template, abort, redirect, url_for, request, Response
# http://flask-sqlalchemy-session.readthedocs.org/en/v1.1/
from flask_sqlalchemy_session import current_session
import ghdiff

from pygameweb.project.models import Project, Release, Tags, top_tags



project_blueprint = Blueprint('project',
                              __name__,
                              template_folder='../templates/')

def project_for(project_id):
    """ gets a project for the given
    """
    result = (current_session
              .query(Project)
              .filter(Project.id == project_id)
              .first())
    # import pdb;pdb.set_trace()
    if not result:
        abort(404)
    return result


def release_for(release_id):
    """ gets a project for the given
    """
    result = (current_session
              .query(Release)
              .filter(Release.id == release_id)
              .first())
    if not result:
        abort(404)
    return result


# @project_blueprint.route('/project/', methods=['GET'])
@project_blueprint.route('/project/<int:project_id>', methods=['GET'])
def view(project_id):
    """ of the wiki page.
    """
    project = project_for(project_id)
    return render_template('project/view.html', project=project)


@project_blueprint.route('/project/<project_id>/<release_id>', methods=['GET'])
@project_blueprint.route('/project/<int:project_id>/<int:release_id>', methods=['GET'])
def release(project_id, release_id):
    """ of the wiki page.
    """
    return render_template('project/view.html',
                           project=project_for(project_id),
                           release=release_for(release_id))


@project_blueprint.route('/tags/<tag>', methods=['GET'])
def tags(tag):
    """ shows the projects for the tag.
    """
    top_tag_counts = top_tags(current_session)

    per_page = 30
    start = int(request.args.get('start', 0))
    prev_start = max(start - per_page, 0)
    next_start = start + per_page

    projects = (current_session
                .query(Project)
                .filter(Tags.project_id == Project.id)
                .filter(Tags.value == tag)
                .offset(start)
                .limit(per_page)
                .all())
    return render_template('project/tags.html',
                           tag=tag,
                           tags=tags,
                           top_tag_counts=top_tag_counts,
                           projects=projects,
                           prev_start=prev_start,
                           next_start=next_start)



def add_project_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(project_blueprint)


