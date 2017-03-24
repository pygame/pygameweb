""" Here we have various jobs.
"""

from subprocess import check_call
from shutil import copy, move
from tempfile import NamedTemporaryFile

from pygameweb.tasks import queue
from pygameweb.config import Config


def compress_png(fname):
    """ with optipng so that it's a bit smaller. Takes a while to process.
    """
    if not fname.endswith('.png'):
        return
    tmp = NamedTemporaryFile(delete=False).name
    copy(fname, tmp)
    check_call(['optipng', '-o7', tmp])
    move(tmp, fname)


if not Config.TESTING:
    # we run the tasks right away in the task runner.
    tasks = queue('default')
    compress_png = tasks.task()(compress_png)


def work():
    queue('default').work()


if __name__ == '__main__':
    work()
