'''scrapes the launchpad html to see if the builds are passing.
'''

import logging
import os
import sys
import time

from pyquery import PyQuery as pq

FAILING = """<svg xmlns="http://www.w3.org/2000/svg" width="81" height="20"><linearGradient id="a" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><rect rx="3" width="81" height="20" fill="#555"/><rect rx="3" x="37" width="44" height="20" fill="#e05d44"/><path fill="#e05d44" d="M37 0h4v20h-4z"/><rect rx="3" width="81" height="20" fill="url(#a)"/><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11"><text x="19.5" y="15" fill="#010101" fill-opacity=".3">build</text><text x="19.5" y="14">build</text><text x="58" y="15" fill="#010101" fill-opacity=".3">failing</text><text x="58" y="14">failing</text></g></svg>"""
PASSING = """<svg xmlns="http://www.w3.org/2000/svg" width="90" height="20"><linearGradient id="a" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><rect rx="3" width="90" height="20" fill="#555"/><rect rx="3" x="37" width="53" height="20" fill="#4c1"/><path fill="#4c1" d="M37 0h4v20h-4z"/><rect rx="3" width="90" height="20" fill="url(#a)"/><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11"><text x="19.5" y="15" fill="#010101" fill-opacity=".3">build</text><text x="19.5" y="14">build</text><text x="62.5" y="15" fill="#010101" fill-opacity=".3">passing</text><text x="62.5" y="14">passing</text></g></svg>"""

def update_build_badge(badge_fname, lanchpad_url):
    '''Updates the badge_fname svg file with the status of the build on lanchpad_url.

    :param lanchpad_url: should be a recipe html url on launchpad.
    :param badge_fname: the svg path with which to update.
                        Only updates badge_fname if build status changes.
    :return: returns True if passing build, False if failing, None if still building.
    '''
    pqd = pq(url=lanchpad_url)
    package_html = pqd('#latest-builds-listing tbody tr.package-build:first').html()
    binary_html = pqd('#latest-builds-listing tbody tr.binary-build:first').html()

    if 'Currently building' in package_html:
        logging.info("still building not updating %s", badge_fname)
        return None

    success = 'Successful build' in package_html and 'Failed to build' not in binary_html
    svg = PASSING if success else FAILING
    success_txt = 'passing' if success else 'failing'

    if os.path.exists(badge_fname):
        with open(badge_fname, 'rb') as badge_file:
            if badge_file.read() == svg:
                logging.info("build %s, not updating %s", success_txt, badge_fname)
                return True
    with open(badge_fname, 'w') as badge_file:
        logging.info("build %s, updating %s", success_txt, badge_fname)
        badge_file.write(svg)
    return True




def check_pygame_builds():
    '''write a badge depending on what the build does.
    '''
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    check_num_times = 5
    # we sleep for 5 minutes, because that seems about the time it takes to build.
    minutes_between_check = 5
    lanchpad_url = 'https://code.launchpad.net/~pygame/+recipe/pygame-daily'
    badge_fname = "frontend/www/images/launchpad_build.svg"

    what_build_did = update_build_badge(badge_fname, lanchpad_url)
    while what_build_did is None and check_num_times > 0:
        logging.info("Build still in progress. Trying %s more times.", check_num_times)
        time.sleep(minutes_between_check * 60)
        what_build_did = update_build_badge("frontend/www/images/launchpad_build.svg", lanchpad_url)
        check_num_times -= 1


if __name__ == "__main__":
    check_pygame_builds()
