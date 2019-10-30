import os
from pathlib import Path
import datetime
from email.utils import formatdate

from flask import (Blueprint, render_template, abort,
                   redirect, url_for, request, current_app,
                   make_response)
from flask_sqlalchemy_session import current_session
from werkzeug.utils import secure_filename
from flask_security import current_user, login_required, roles_required

from pygameweb.project.models import (
    Project, Release, Tags, top_tags, recent_releases
)
from pygameweb.project.forms import (
    FirstReleaseForm,
    ReleaseForm,
    ProjectForm,
    ProjectCommentForm,
    ReleaseDeleteForm,
)
from pygameweb.comment.models import CommentPost, CommentAuthor, CommentThread
from pygameweb.sanitize import sanitize_html
from pygameweb.comment.classifier import classify_comment
from pygameweb.user.models import User


project_blueprint = Blueprint('project',
                              __name__,
                              template_folder='../templates/')


def project_for(project_id):
    """ gets a project for the given
    """
    project = (current_session
               .query(Project)
               .filter(Project.id == project_id)
               .first())
    if project is None:
        abort(404)
    if project.user and project.user.disabled != 0:
        abort(404)

    return project


def release_for(release_id):
    """ gets a project for the given
    """
    release = (current_session
              .query(Release)
              .filter(Release.id == release_id)
              .first())
    if not release:
        abort(404)
    if release.project.user and release.project.user.disabled != 0:
        abort(404)
    return release


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
@project_blueprint.route('/project/<int:project_id>/', methods=['GET'])
@project_blueprint.route('/project/<int:project_id>', methods=['GET'])
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
@project_blueprint.route('/project/<int:project_id>/<int:release_id>/',
                         methods=['GET'])
@project_blueprint.route('/project/<int:project_id>/<int:release_id>',
                         methods=['GET'])
def release(project_id, release_id, title=None):
    """ of the release page.
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
    prev_start = start - per_page
    if prev_start < 0:
        prev_start = None
    next_start = start + per_page

    # all is a special tag, meaning show all.
    if tag == 'all':
        projectsq = (current_session
                     .query(Project)
                     .join(User)
                     .join(Release)
                     .filter(Release.project_id == Project.id)
                     .filter(User.id == Project.users_id)
                     .filter(User.disabled == 0)
                     .order_by(Release.datetimeon.desc()))
    else:
        projectsq = (current_session
                     .query(Project)
                     .join(User)
                     .join(Tags)
                     .filter(User.id == Project.users_id)
                     .filter(User.disabled == 0)
                     .filter(Tags.project_id == Project.id)
                     .filter(Tags.value == tag))

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


@project_blueprint.route('/tags/', methods=['GET'])
@project_blueprint.route('/tags', methods=['GET'])
def all_tags():
    """ On this view we list ALL the tags.
    """
    tag_counts = top_tags(current_session, limit=None)
    return render_template('project/tags_view.html',
                           tag_counts=tag_counts,
                           title='Tags')


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


@project_blueprint.route('/project/<int:project_id>/comment',
                         methods=['GET', 'POST'])
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

        # we have proxy fix for remote_addr.
        ip_address = request.remote_addr
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
        if classify_comment(post) == 'spam':
            post.is_spam = True

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
            user=user,
            youtube_trailer=form.youtube_trailer.data,
            github_repo=form.github_repo.data,
            patreon=form.patreon.data,
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
        project.youtube_trailer = form.youtube_trailer.data
        project.github_repo = form.github_repo.data
        project.patreon = form.patreon.data

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


@project_blueprint.route(
    '/members/projects/<int:project_id>/releases/delete/<int:release_id>',
    methods=['GET', 'POST']
)
@login_required
@roles_required('members')
def delete_release(project_id, release_id):
    """

    on post, delete the release.
    on get, show a form for posting to delete it.
    """
    project = project_for(project_id)
    if project.user.id != current_user.id:
        abort(404)
    if release_id is not None:
        arelease = release_for(release_id)
        if arelease.project.user.id != current_user.id:
            abort(404)

    if request.method == 'GET' and release_id is not None:
        form = ReleaseDeleteForm(obj=arelease)
    else:
        form = ReleaseDeleteForm()

    if form.validate_on_submit():
        (current_session
            .query(Release)
            .filter(Release.id == release_id)
            .delete()
        )
        current_session.commit()
        return redirect(url_for('project.releases', project_id=project.id))

    return render_template(
        'project/deleterelease.html',
        form=form,
        project_for=project_for,
        release_for=release_for,
        project_id=project_id,
        release_id=release_id
    )

def feed_recent_releases():
    """ of projects to the rss and atom robots.
    """
    return recent_releases(current_session).limit(20).all()


@project_blueprint.route('/project/feed/atom', methods=['GET'])
def atom():
    """ of recent releases
    """
    resp = render_template('project/atom.xml',
                           recent_releases=feed_recent_releases())
    response = make_response(resp)
    content_type = 'application/atom+xml; charset=utf-8; filename=news-ATOM'
    response.headers['Content-Type'] = content_type
    return response


@project_blueprint.route('/project/feed/rss', methods=['GET'])
def rss():
    """ of recent releases
    """
    build_date = formatdate(datetime.datetime.now().timestamp())
    resp = render_template('project/rss.xml',
                           recent_releases=feed_recent_releases(),
                           build_date=build_date)
    response = make_response(resp)
    content_type = 'application/xml; charset=ISO-8859-1; filename=news-RSS2.0'
    response.headers['Content-Type'] = content_type
    return response


@project_blueprint.route('/feed/releases.php', methods=['GET'])
def legacy_feeds():
    feed_type = request.args.get('format', 'ATOM')
    if feed_type == 'ATOM':
        return atom()
    elif feed_type == 'RSS2.0':
        return rss()
    return ''


def add_project_blueprint(app):
    """ to the app.
    """
    app.register_blueprint(project_blueprint)
