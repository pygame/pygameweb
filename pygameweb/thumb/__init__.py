"""
"""

from hashlib import md5
from pathlib import Path
import os
import subprocess


def compress_later(fname):
    """ If we can compress the thumbnail later.

    :param fname: filename to compress.
    """
    from pygameweb.tasks.worker import compress_png
    compress_png(fname)


def image_thumb(www_path: Path,
                fname,
                width: int,
                height: int,
                itype="jpg",
                quality: int=80):
    """Get the thumbnail fname. Make a thumbnail the image if it is not there.

    :param www_path: where the thumbnails live.
    :param fname: File name of image
    :param width: Max width
    :param height: Max height
    :return: Thumbnail name

    :Example:
    image_thumb('./frontend/www/', '1.jpg', 100, 100)
    """
    if fname is None:
        return None

    shots_path = www_path / 'shots'
    thumb_path = www_path / 'thumb'
    image = shots_path / fname
    if '..' in fname:
        raise ValueError('wat')

    try:
        filesize = os.path.getsize(image)
    except FileNotFoundError:
        return

    imagel = str(image).lower()
    if imagel.endswith('.jpg'):
        itype = 'jpg'
    elif imagel.endswith('.png'):
        itype = 'png'

    the_string = f'thumb {fname} {width} {height} {filesize}'.encode('utf-8')
    hash_fname = md5(the_string).hexdigest() + '.' + itype
    dest = str(thumb_path / hash_fname)

    if not os.path.exists(dest):
        cmd = ['convert',
               '-quality',
               str(quality),
               str(image),
               '-resize',
               f'{width}x{height}',
               '+profile',
               '"*"',
               dest]
        subprocess.check_call(cmd)
        compress_later(dest)

    return f'/thumb/{hash_fname}'
