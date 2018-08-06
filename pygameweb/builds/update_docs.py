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

    update_file = pygame_dir / 'docs/reST/themes/classic/elements.html'

    assert www.exists()
    assert pygame_dir.exists()
    assert venv_python.exists()
    assert update_file.exists()

    run(['touch', str(update_file)], cwd=cwd)
    run(['git', 'pull'], cwd=cwd)
    run([str(venv_python.absolute()), 'setup.py', 'docs'], cwd=cwd)
    run(['rsync', '-va', '--delete', 'docs/',
         str(docs_path.absolute())], cwd=cwd)
