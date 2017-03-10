""" Generates server.json for the hifi website.

This contains legacy SQL code which needs to be rewritten using the models.
Not doing this now so this task doesn't block the new website being used.
"""

import sys, os, glob, re
import feedparser
#import pymysql as MySQLdb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import json, datetime
import xml.sax.saxutils

import pygameweb
from pygameweb.config import Config
from pygameweb.wiki.wiki import render as wiki_render
from pygameweb.wiki.models import Wiki


def create_session(verbose=False):
    """ returns a db session.
    """
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=verbose)
    return sessionmaker(bind=engine)()


def __utf8(value):
    if isinstance(value, unicode):
        return value.encode("utf-8")
    assert isinstance(value, str)
    return value


def qhtml(value):
    """ qhtml(value) returns an html encoded value.

        >>> qhtml(">")
        '&gt;'
        >>> qhtml("a")
        'a'
        >>> qhtml(u"a")
        'a'
    """
    return __utf8(xml.sax.saxutils.escape(value))


def sanitise_html(html):
    """ santise_html(html) returns some sanitised html.
          It can be used to try and avoid basic html insertion attacks.

        >>> sanitise_html("<p>hello</p>")
        '<p>hello</p>'
        >>> sanitise_html("<script>alert('what')</script>")
        ''
    """
    return feedparser._sanitizeHTML(html, "utf-8", "text/html")


def strip_html(text):
    """ makes sure there is no html in the given text.
        >>> strip_html("<p>hello</p>")
        '&lt;p&gt;hello&lt;/p&gt;'
        >>> strip_html("<script>alert('what')</script>")
        ''
    """
    # try and clear any dangerous stuff from it.

    try:
        shtml = sanitise_html(text)
    except AttributeError:
        raise ValueError("problem sanitising :%s:" % (repr(text)))

    # encode what we have into html
    try:
        return qhtml(shtml)
    except AttributeError:
        raise ValueError("problem stripping :%s:" % (repr(text)))


TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)


def isnumber(n):
    return isinstance(n, (int, float, complex))


def sanitise_the_rows(rows, except_for_keys=None):
    """ sanitises the values in all of the rows, for html.
        Do not sanitise the keys named in except_for_keys
    """
    sanitised_rows = []
    if except_for_keys is None:
        except_for_keys = []

    for row in rows:
        new_r = {}
        for key, val in row.items():
            if key in except_for_keys:
                new_r[key] = val
            else:
                if isnumber(val):
                    new_r[key] = int(val)
                elif val is None:
                    new_r[key] = val
                elif type(val) == datetime.datetime:
                    new_r[key] = val.strftime("%B %d, %Y")
                else:
                    new_r[key] = sanitise_html(val)
        sanitised_rows.append(new_r)
    return sanitised_rows

#dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
def dthandler(obj):
    """For turning dates into iso format dates.
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        raise TypeError("%s is not JSON serializable" % obj)


class GenerateJson(object):
    """ Generates the server.json
    """

    def __init__(self, www_path, json_fname):
        """

        :param www_path: where the www files live.
        :param json_fname: where the json should be put.
        """
        self.www_path = www_path
        self.fname = json_fname

        output = self.generate_json()
        stack_json_path = os.path.join(self.www_path, "stackexchange.json")
        with open(stack_json_path) as jsonf:
            output["stackexchange"] = json.load(jsonf)
        with open(self.fname, "w") as afile:
            json.dump(output, afile, default=dthandler, indent=4)


    def generate_json(self):
        """ generate_json() returns dict ready for saving to json.
        """
        table_rows = {}

        news = {}
        release = {}
        spotlight = {}
        wiki = {}
        music = {}


        session = create_session(verbose=False)

        sql = "SELECT * from news ORDER BY datetimeon DESC LIMIT 10"

        rows = [dict(row) for row in session.execute(sql, ())]

        table_rows['news'] = sanitise_the_rows(rows)
        for row in table_rows['news']:
            news[row['id']] = row

        sql = """SELECT users.id as users_id, users.name as users_name, users.title as users_title,

                        project.id as project_id, project.users_id as project_users_id, project.node_id as project_node_id,
                        project.description as project_description,project.summary as project_summary,
                        project.title as project_title,project.image as project_image,

                        release.datetimeon as datetimeon, release.version as title, release.id as id

                 FROM users,project,release
                 WHERE release.project_id = project.id AND users.id=project.users_id

                 ORDER BY release.datetimeon DESC LIMIT 36"""

        rows = [dict(row) for row in session.execute(sql, ())]

        table_rows["release"] = sanitise_the_rows(rows, except_for_keys=[])
        for i, row in enumerate(table_rows['release']):
            row['project_summary'] = remove_tags(row['project_summary'])
            release[i] = row



        # spotlight ids.
        if "spotlight ids":
            sids = []
            sids += [33] # outerspace
            sids += [123, 126, 124] #dynamite, quido, pylonoid
            sids += [120] #the witchs yarn
            sids += [181, 163] #angry drunken dwarves, galaxy mage
            sids += [238, 235, 237] #pyweek2: nelly's garden, funnyboat, 20000 light years
            sids += [306, 300, 308] #pyweek3: typus pokus, wijafjord, bouncy
            sids += [406, 415] #pyweek4: barbie seahorse, woody tigerbalm
            sids += [487, 498] #pyweek5: Disk Field, 555-BOOM

            #ardentryst, plague, bubbmman 2, mastermind, food force
            sids += [596, 991, 1114, 859, 1122]
            #paintbrush, pixelpaint, arcade tonk tanks, toonloop
            sids += [1280, 1245, 1078, 1310]

            #sids += [2086, 2064, 2075] # pygamezine, Life as a Bit, QANAT
            sids += [2064, 2075] # Life as a Bit, QANAT
            # Making Games with Python & Pygame, SubTerrex, PyTuner: A Guitar Tuner In Pygame
            sids += [2404, 2389, 2401]
            # Program Arcade Games With Python and Pygame, Albow, SGC, glLib Reloaded
            sids += [2843, 338, 2089, 1326]

            sids_sql = ",".join([str(x) for x in sids])


            # Get the latest release for each of the spotlight ids.
            sql = """
            SELECT users.id as users_id, users.name as users_name, users.title as users_title,
                   project.id as project_id, project.users_id as project_users_id, project.node_id as project_node_id,
                   project.description as project_description, project.summary as project_summary,
                   project.title as project_title, project.image as project_image,

                        release.datetimeon as datetimeon, release.version as title, release.id as id

                 FROM users,project,release
                 WHERE release.project_id = project.id AND users.id=project.users_id

                 AND release.id in (SELECT tt.id
                    FROM release tt
                    INNER JOIN
                        (SELECT project_id, MAX(datetimeon) AS MaxDateTime
                        FROM release
                        where release.project_id in (%s)
                        GROUP BY project_id) groupedtt
                    ON tt.project_id = groupedtt.project_id
                    AND tt.datetimeon = groupedtt.MaxDateTime)

                 ORDER BY release.datetimeon DESC LIMIT 36""" % (sids_sql)
            #print sql

            rows = [dict(row) for row in session.execute(sql, ())]

            table_rows["spotlight"] = sanitise_the_rows(rows, except_for_keys=[])
            for i, row in enumerate(table_rows['spotlight']):
                row['project_summary'] = remove_tags(row['project_summary'])
                spotlight[i] = row

        # music player info.
        music = {0: ""}


        links = "index about tutorials CookBook resources info Hacking".split()
        links_sql = "".join(["'%s'," % l for l in links])[:-1]
        sql = """SELECT * from wiki WHERE latest=1 AND link in (%s)""" % (links_sql)
        rows = [dict(row) for row in session.execute(sql, ())]

        table_rows['wiki'] = sanitise_the_rows(rows, except_for_keys=["content"])

        def for_link(link):
            return Wiki.content_for_link(session, link)

        for i, row in enumerate(table_rows['wiki']):
            row['content'] = wiki_render(row['content'], for_link)
            row['content'] = sanitise_html(row['content'])
            wiki[row['link']] = row


        output = {}
        output['news'] = news
        output['release'] = release
        output['wiki'] = wiki
        output['spotlight'] = spotlight
        output['music'] = music

        return output


def main():
    # www_path = os.path.join(os.path.split(pygameweb.__file__)[0], '..', 'www')
    www_path = os.path.join('frontend', 'www')
    json_path = os.path.join(www_path, 'server.json')
    GenerateJson(www_path, json_path)
    sys.exit(0)


if __name__ == "__main__":


    if "--test" in sys.argv:
        def _test():
            import doctest
            doctest.testmod()
        _test()

    else:
        main()
