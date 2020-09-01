""" pygameweb
"""
import io
import os
import re
from itertools import chain

from setuptools import setup, find_packages


def read(*parts):
    """ Reads in file from *parts.
    """
    try:
        return io.open(os.path.join(*parts), 'r', encoding='utf-8').read()
    except IOError:
        return ''


def get_version():
    """ Returns version from pygameweb/__init__.py
    """
    version_file = read('pygameweb', '__init__.py')
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]',
                              version_file, re.MULTILINE)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


def get_requirements():
    """ returns list of requirements from requirements.txt files.
    """
    fnames = ['requirements.txt']
    requirements = chain.from_iterable((open(fname) for fname in fnames))
    requirements = list(set([l.strip() for l in requirements]) - {'-r requirements.txt'})
    return requirements


setup(
    name='pygameweb',
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    data_files=[('.', ['alembic.ini'])],
    license='BSD',
    author='Rene Dudfield',
    author_email='renesd@gmail.com',
    description='Pygame.org website.',
    include_package_data=True,
    long_description=read('README.rst'),
    package_dir={'pygameweb': 'pygameweb'},
    packages=find_packages(),
    package_data={'pygameweb': []},
    url='https://github.com/pygame/pygameweb',
    install_requires=get_requirements(),
    version=get_version(),
    entry_points={
        'console_scripts': [
            'pygameweb_front='
                'pygameweb.run:run_front',
            'pygameweb_generate_json='
                'pygameweb.dashboard.generate_json:main',
            'pygameweb_generate_static='
                'pygameweb.dashboard.generate_static:main',
            'pygameweb_launchpad='
                'pygameweb.builds.launchpad_build_badge:check_pygame_builds',
            'pygameweb_update_docs='
                'pygameweb.builds.update_docs:update_docs',
            'pygameweb_stackoverflow='
                'pygameweb.builds.stackoverflow:download_stack_json',
            'pygameweb_loadcomments='
                'pygameweb.comment.models:load_comments',
            'pygameweb_trainclassifier='
                'pygameweb.comment.classifier_train:classify_comments',
            'pygameweb_worker='
                'pygameweb.tasks.worker:work',
            'pygameweb_release_version_correct='
                'pygameweb.builds.update_version_from_git:release_version_correct',
            'pygameweb_github_releases='
                'pygameweb.project.gh_releases:sync_github_releases',
            'pygameweb_fixtures=' +
                'pygameweb.fixtures:populate_db',
        ],
    },
)
