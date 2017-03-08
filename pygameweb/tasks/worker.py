"""Here we have various jobs.
"""

from pygameweb.tasks import queue
from pygameweb.config import Config
from sqlalchemy import create_engine

def work():
    name = 'default'

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    the_queue = queue(name, engine=engine)
    for job in the_queue[name]:
        print(job)

if __name__ == '__main__':
    work()
