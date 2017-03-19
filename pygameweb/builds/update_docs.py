""" Updates the docs.

Assumes there is a pygame repo living parallel to a pygameweb one.
"""
import sys
from subprocess import run
from pathlib import Path


def update_docs():
    """From the pygame repo, update the docs in
       pygame/pygameweb/frontend/www/docs/
    """

    pygame_dir = Path('..') / 'pygame'
    venv_python = Path(sys.executable)
    www = Path('.') / 'frontend/www/'
    docs_path = www / 'docs'
    cwd = str(pygame_dir.absolute())

    assert www.exists()
    assert pygame_dir.exists()
    assert venv_python.exists()

    run(['hg', 'pull'], cwd=cwd)
    run(['hg', 'update'], cwd=cwd)
    run([str(venv_python.absolute()), 'makeref.py'], cwd=cwd)
    run(['rsync', '-va', '--delete', 'docs/',
         str(docs_path.absolute())], cwd=cwd)
