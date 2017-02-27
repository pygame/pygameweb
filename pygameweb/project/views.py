import os
from pathlib import Path
import datetime

from flask import Blueprint, render_template, abort, redirect, url_for, request, Response, current_app
# http://flask-sqlalchemy-session.readthedocs.org/en/v1.1/
from flask_sqlalchemy_session import current_session
import ghdiff
from werkzeug.utils import secure_filename
from flask_security import current_user, login_required, roles_required


from pygameweb.user.models import User
from pygameweb.project.models import Project, Release, Tags, top_tags
from pygameweb.project.forms import FirstReleaseForm, ReleaseForm, ProjectForm


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



@project_blueprint.route('/projects', methods=['GET'])
def projects():
    return render_template('project/projects.html', projects=[])


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

# members/projects/
# http://pygame.org/members/projects/new/new.php?&_id=7ac085095c01e07e633302581e829dfd

def save_image(form_field, image_path):
    """ A little helper to save images.
    """
    return form_field.data.save(image_path)


@roles_required('member')
@project_blueprint.route('/members/projects/new', methods=['GET', 'POST'])
def new_project():
    """ This adds both a project, and a release.
    """
    form = FirstReleaseForm()

    if form.validate_on_submit():

        www = Path(current_app.config['WWW'])
        sec_fname = secure_filename(form.image.data.filename)
        extension = os.path.splitext(sec_fname)[-1]
        now = datetime.datetime.now()

        user = current_user
        project = Project(
            title=form.title.data,
            summary=form.summary.data,
            description=form.description.data,
            uri=form.uri.data,
            datetimeon=now,
            user=user
        )
        release = Release(datetimeon=now,
                          description=form.description.data,
                          srcuri=form.srcuri.data,
                          winuri=form.winuri.data,
                          macuri=form.macuri.data,
                          version=form.version.data)
        project.releases.append(release)

        tags = [t.lstrip().rstrip() for t in form.tags.data.split(',')]
        for tag in tags:
            current_session.add(Tags(project=project, value=tag))

        current_session.add(project)
        current_session.commit()

        image_fname = f'{project.id}{extension}'
        project.image = image_fname
        current_session.add(project)
        image_path = str(www / 'shots' / image_fname)

        save_image(form.image, image_path)
        current_session.commit()

        return redirect(url_for('project.view', project_id=project.id))

    return render_template('project/newproject.html', form=form)


@roles_required('member')
@project_blueprint.route('/members/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    form = ProjectForm()

    if form.validate_on_submit():

        project = project_for(project_id)
        if project.user.id != current_user.id:
            abort(404)

        project.title = form.title.data
        project.summary = form.summary.data
        project.description = form.description.data
        project.uri = form.uri.data
        project.datetimeon = datetime.datetime.now()

        for tag in (current_session
                    .query(Tags)
                    .filter(Tags.project_id == project.id)
                    .all()):
            current_session.delete(tag)

        tags = [t.lstrip().rstrip() for t in form.tags.data.split(',')]
        for tag in tags:
            current_session.add(Tags(project=project, value=tag))

        current_session.add(project)
        current_session.commit()

        if form.image.data is not None:
            www = Path(current_app.config['WWW'])
            sec_fname = secure_filename(form.image.data.filename)
            extension = os.path.splitext(sec_fname)[-1]

            image_fname = f'{project.id}{extension}'
            project.image = image_fname
            current_session.add(project)
            image_path = str(www / 'shots' / image_fname)

            save_image(form.image, image_path)
            current_session.commit()

        return redirect(url_for('project.view', project_id=project.id))

    return render_template('project/editproject.html', form=form, project_id=project_id)


@roles_required('member')
@project_blueprint.route('/members/projects/<int:project_id>/releases/new',
                         methods=['GET', 'POST'],
                         defaults={'release_id':None})
@project_blueprint.route('/members/projects/<int:project_id>/releases/edit/<int:release_id>', methods=['GET', 'POST'])
def edit_release(project_id, release_id):
    form = ReleaseForm()

    if form.validate_on_submit():
        project = project_for(project_id)
        if project.user.id != current_user.id:
            abort(404)

        if release_id is None:
            release = Release(datetimeon=datetime.datetime.now(),
                              description=form.description.data,
                              srcuri=form.srcuri.data,
                              winuri=form.winuri.data,
                              macuri=form.macuri.data,
                              version=form.version.data)
            project.releases.append(release)
            current_session.add(project)
        else:
            release = release_for(release_id)

            release.datetimeon = datetime.datetime.now()
            release.description = form.description.data
            release.srcuri = form.srcuri.data
            release.winuri = form.winuri.data
            release.macuri = form.macuri.data
            release.version = form.version.data
            current_session.add(release)

        current_session.commit()

        return redirect(url_for('project.release', project_id=project_id, release_id=release.id))

    return render_template('project/editrelease.html',
                           form=form,
                           project_id=project_id,
                           release_id=release_id)




def add_project_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(project_blueprint)


