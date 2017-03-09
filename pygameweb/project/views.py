import os
from pathlib import Path
import datetime

from flask import (Blueprint, render_template, abort,
                   redirect, url_for, request, current_app)
from flask_sqlalchemy_session import current_session
from werkzeug.utils import secure_filename
from flask_security import current_user, login_required, roles_required

from pygameweb.project.models import Project, Release, Tags, top_tags
from pygameweb.project.forms import (FirstReleaseForm,
                                     ReleaseForm,
                                     ProjectForm,
                                     ProjectCommentForm)
from pygameweb.comment.models import CommentPost, CommentAuthor, CommentThread
from pygameweb.sanitize import sanitize_html

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


def comments_for(project_id):
    forum = 'pygame'
    id_text = f'pygame_project_{project_id}'
    return CommentPost.for_thread(current_session, forum, id_text)


@project_blueprint.route('/members/projects', methods=['GET'])
@login_required
@roles_required('members')
def projects():
    """ shows a list of projects for the user.
    """
    projects = (current_session
                .query(Project)
                .filter(Project.users_id == current_user.id)
                .all())

    return render_template('project/projects.html', projects=projects)


@project_blueprint.route('/members/projects/<int:project_id>/releases',
                         methods=['GET'])
@login_required
@roles_required('members')
def releases(project_id):
    project = (current_session
               .query(Project)
               .filter(Project.id == project_id)
               .filter(Project.users_id == current_user.id)
               .first())
    if not project:
        abort(404)

    return render_template('project/releases.html',
                           releases=project.releases,
                           project=project)


# project-Rotating+3D+Cube-1859-.html
@project_blueprint.route('/project-<path:title>-<int:project_id>-.html',
                         methods=['GET'])
@project_blueprint.route('/project/<int:project_id>', methods=['GET'])
@project_blueprint.route('/project/<int:project_id>/', methods=['GET'])
def view(project_id, title=None):
    """ of the wiki page.
    """
    release_id = request.args.get('release_id', None)
    if release_id is not None:
        return release(project_id, int(release_id))

    return render_template('project/view.html',
                           project_id=project_id,
                           project_for=project_for,
                           commentform=ProjectCommentForm(),
                           comments_for=comments_for)


# project-pyChessClock-1695-2948.html
@project_blueprint.route('/project-<path:title>-<int:project_id>'
                         '-<int:release_id>.html',
                         methods=['GET'])
@project_blueprint.route('/project/<int:project_id>/<int:release_id>',
                         methods=['GET'])
def release(project_id, release_id, title=None):
    """ of the wiki page.
    """
    return render_template('project/view.html',
                           project_for=project_for,
                           release_for=release_for,
                           project_id=project_id,
                           release_id=release_id,
                           commentform=ProjectCommentForm(),
                           comments_for=comments_for)


def inchunks(alist, chunk_size):
    """ Splits a list up into chunks of chunk_size.

        [1,2,3, 4,5,6] -> [[1,2,3], [4,5,6]]
    """
    for i in range(0, len(alist), chunk_size):
        yield alist[i:i + chunk_size]


@project_blueprint.route('/tags/<tag>', methods=['GET'])
def tags(tag):
    """ shows the projects for the tag.
    """
    top_tag_counts = top_tags(current_session)

    per_page = 30
    start = int(request.args.get('start', 0))
    prev_start = max(start - per_page, 0)
    next_start = start + per_page

    projectsq = (current_session
                 .query(Project)
                 .filter(Tags.project_id == Project.id))
    # all is a special tag, meaning show all.
    if tag != 'all':
        projectsq = projectsq.filter(Tags.value == tag)

    projects = (projectsq
                .offset(start)
                .limit(per_page)
                .all())

    return render_template('project/tags.html',
                           tag=tag,
                           tags=tags,
                           top_tag_counts=top_tag_counts,
                           projects=inchunks(projects, 3),
                           prev_start=prev_start,
                           next_start=next_start)


"""
  <post dsq:id="194253444">
    <id/>
    <message>&lt;p&gt;Some X message ok.&lt;/p&gt;</message>
    <createdAt>2011-04-29T17:39:31Z</createdAt>
    <isDeleted>false</isDeleted>
    <isSpam>false</isSpam>
    <author>
      <email>a@example.com</email>
      <name>Some name a</name>
      <isAnonymous>false</isAnonymous>
      <username>blablax</username>
    </author>
    <ipAddress>2.2.2.2</ipAddress>
    <thread dsq:id="291436086"/>
    <parent dsq:id="194253320"/>
  </post>
"""

@project_blueprint.route('/project/<int:project_id>/comment', methods=['GET', 'POST'])
@login_required
@roles_required('members')
def new_comment(project_id):
    """ Post a comment on this project.
    """
    form = ProjectCommentForm()

    if form.validate_on_submit():
        project = project_for(project_id)
        author = CommentAuthor.from_user(current_session, current_user)
        parent_id = int(form.parent_id.data) if form.parent_id.data else None
        thread_id = int(form.thread_id.data) if form.thread_id.data else None
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        created_at = datetime.datetime.now()

        # hardcoded pygame forum id.
        category = '796386'
        forum = 'pygame'
        title = project.title
        link = f'https://pygame.org/project/{project_id}/'
        id_text = f'pygame_project_{project_id}'
        message = form.message.data
        message = message if '<p>' not in message else f'<p>{message}</p>'

        if not thread_id:
            thread = CommentThread(
                id_text=id_text,
                forum=forum,
                category=category,
                link=link,
                title=title,
                ip_address=ip_address,
                author=author,
                created_at=created_at,
                is_closed=False,
                is_deleted=False,
            )
            current_session.add(thread)

        post = CommentPost(author=author,
                           parent_id=parent_id,
                           message=sanitize_html(message),
                           ip_address=ip_address,
                           created_at=created_at,
                           is_deleted=False,
                           is_spam=False)
        if thread_id is None:
            post.thread = thread
        else:
            post.thread_id = thread_id

        current_session.add(post)
        current_session.commit()

    return redirect(url_for('project.view', project_id=project_id))


def save_image(form_field, image_path):
    """ A little helper to save images.
    """
    return form_field.data.save(image_path)


@project_blueprint.route('/members/projects/new', methods=['GET', 'POST'])
@login_required
@roles_required('members')
def new_project():
    """ This adds both a project, and a release.
    """
    form = FirstReleaseForm()

    if form.validate_on_submit():

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

        tags = [t.lstrip().rstrip() for t in form.tags.data.split(',')]
        if '' in tags:
            tags.remove('')

        for value in tags:
            tag = Tags(project=project, value=value)
            current_session.add(tag)

        release = Release(datetimeon=now,
                          description=form.description.data,
                          srcuri=form.srcuri.data,
                          winuri=form.winuri.data,
                          macuri=form.macuri.data,
                          version=form.version.data)
        project.releases.append(release)

        if form.image.data is not None:
            www = Path(current_app.config['WWW'])
            sec_fname = secure_filename(form.image.data.filename)
            extension = os.path.splitext(sec_fname)[-1]

            current_session.commit()
            image_fname = f'{project.id}{extension}'
            project.image = image_fname
            image_path = str(www / 'shots' / image_fname)

            save_image(form.image, image_path)

        current_session.add(project)
        current_session.commit()

        return redirect(url_for('project.view', project_id=project.id))

    return render_template('project/newproject.html', form=form)


@project_blueprint.route('/members/projects/edit/<int:project_id>',
                         methods=['GET', 'POST'])
@login_required
@roles_required('members')
def edit_project(project_id):
    project = project_for(project_id)
    if project.user.id != current_user.id:
        abort(404)

    if request.method == 'GET':
        form = ProjectForm(obj=project)
        form.tags.data = ','.join([t.value for t in project.tags])
        form.image.data = ''
    else:
        form = ProjectForm()

    if form.validate_on_submit():

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
        if '' in tags:
            tags.remove('')

        for value in tags:
            tag = Tags(project=project, value=value)
            current_session.add(tag)

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

    return render_template('project/editproject.html',
                           form=form,
                           project_id=project_id)


@project_blueprint.route('/members/projects/<int:project_id>/releases/new',
                         methods=['GET', 'POST'],
                         defaults={'release_id': None})
@project_blueprint.route('/members/projects/<int:project_id>/'
                         'releases/edit/<int:release_id>',
                         methods=['GET', 'POST'])
@login_required
@roles_required('members')
def edit_release(project_id, release_id):
    """ or create a new release if release_id is None.
    """
    project = project_for(project_id)
    if project.user.id != current_user.id:
        abort(404)
    if release_id is not None:
        release = release_for(release_id)
        if release.project.user.id != current_user.id:
            abort(404)

    if request.method == 'GET' and release_id is not None:
        form = ReleaseForm(obj=release)
    else:
        form = ReleaseForm()

    if form.validate_on_submit():

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
            release.datetimeon = datetime.datetime.now()
            release.description = form.description.data
            release.srcuri = form.srcuri.data
            release.winuri = form.winuri.data
            release.macuri = form.macuri.data
            release.version = form.version.data
            current_session.add(release)

        current_session.commit()

        return redirect(url_for('project.release',
                                project_id=project_id,
                                release_id=release.id))

    return render_template('project/editrelease.html',
                           form=form,
                           project_id=project_id,
                           release_id=release_id)


@project_blueprint.route('/members/projects/<int:project_id>/'
                         'releases/delete/<int:release_id>',
                         methods=['GET', 'POST'])
@login_required
@roles_required('members')
def delete_release(project_id, release_id):
    """

    on post, delete the release.
    on get, show a form for posting to delete it.
    """
    raise NotImplementedError()


def add_project_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(project_blueprint)
