"""Here we have various jobs.
"""

from pygameweb.tasks import queue
from pygameweb.db import _get_session

def work():
    name = 'default'
    the_queue = queue(name, _get_session())
    for job in the_queue[name]:
        print(job)




if __name__ == '__main__':
    work()
