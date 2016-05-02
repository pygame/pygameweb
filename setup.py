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
        'Classifier: Framework :: Flask',
        'Classifier: License :: OSI Approved',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    data_files=[('.', ['alembic.ini'])],
    license='TODO',
    author='pygame',
    author_email='',
    description='Pygame.org website.',
    include_package_data=True,
    long_description=read('README.rst'),
    package_dir={'pygameweb': 'pygameweb'},
    packages=find_packages(),
    package_data={'pygameweb': []},
    url='https://bitbucket.org/pygame/pygameweb',
    install_requires=get_requirements(),
    version=get_version(),
)
