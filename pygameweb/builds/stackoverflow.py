""" Stackoverflow related things.
"""
import os
import sys

def download_stack_json():
    """ Downloads some question and answer info.
    """
    import pygameweb.config
    stack_key = pygameweb.config.Config.STACK_KEY
    url = (f"'https://api.stackexchange.com/2.2/search?key={stack_key}"
           "((&site=stackoverflow&order=desc&sort=activity&tagged=pygame&filter=default'")

    cmd = ' '.join(['curl', url, '-s', '--compressed', '>', '/tmp/stackexchange.json'])
    cmd2 = ' '.join(['mv', '/tmp/stackexchange.json', 'frontend/www/'])
    ret = os.system(cmd)
    if ret != 0:
        raise RuntimeError(f'cmd failed:{cmd}')
    ret2 = os.system(cmd2)
    if ret2 != 0:
        raise RuntimeError(f'cmd2 failed:{cmd2}')
    sys.exit(0)
