__version__ = '0.0.4'


# So we can use environment variables to configure things.

def load_into_environ(fname):
    """ load the key value pairs in fname into the os.environ.

    Each line should have a key=value pair.
    There can be comments with #.

    :param fname: name of the '.env' file.
    """
    import os

    def as_key_value(lines):
        """ Return a dict of the key value pairs.
        """
        no_comments = [l.split('#')[0].rstrip() for l in lines if not l.startswith('#')]
        no_empty = [l for l in no_comments if l]
        kvs = [l.split('=') for l in no_empty]
        no_extra_spaces = [(k.rstrip().lstrip(), v.rstrip().lstrip()) for k, v in kvs]
        return no_extra_spaces

    if os.path.exists(fname):
        with open(fname) as lines:
            for key, value in as_key_value(lines):
                if key not in os.environ:
                    os.environ[key] = value

load_into_environ('.env')
