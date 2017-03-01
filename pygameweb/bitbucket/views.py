"""bitbucket.org related things.
"""
import subprocess

def add_bitbucket(app):
    """ to the app.
    """
    @app.route('/bitbucket', methods=['POST'])
    def bitbucket(self, **kwargs):
        cmd = '/home/pygame/bin/bitbucket_updated.sh'
        subprocess.run(cmd)
        return "sweet"
