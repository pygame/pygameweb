"""For all the static parts of the website. css, js, html.
"""

import os, sys, glob, json, tempfile, argparse, subprocess
import urllib.request

# to regenerate all the files.
# python generate_static.py --parse_urls=

_logit = False
def log(x):
    global _logit
    if _logit:
        print (x)

class Urls(object):
    #
    #def __init__(self, base_url, www_path, json_path,
    #                cleanup_tmp_files_at_start,
    #                cleanup_tmp_files_at_end):


    def __init__(self, config):
        log (config)
        for k,v in config.items():
            setattr(self, k, v)

        if self.minify:
            if "js" in self.minify:
                self.compress_javascript()
            if "css" in self.minify:
                self.compress_css()
            return


        self.temp_prefix = "tmpfile_"

        self.data = json.load(open(self.json_path))


        #self.urls = self.generateAllUrls(self.parse_urls)
        # self.urls = ["hifi.html"]
        self.urls = ["dashboard-dev"]



        #us = [u for u in self.urls if u in ["designer-xxx.html"]]
        us = self.urls

        log ("generating these urls:%s" % us)

        #self.cleanup_at_start(self.urls)
        self.generateFiles(us)



    def cleanup_at_start(self, urls_to_remove):
        # remove any existing tmpfiles.
        if self.cleanup_tmp_files_at_start:
            for f in glob.glob(os.path.join(self.www_path, "tmpfile_*")):
                os.remove(f)

        # remove all of the html files.
        if self.remove_all_html:
            for f in glob.glob(os.path.join(self.www_path, "*.html")):
                os.remove(f)

        # remove the given urls
        if self.remove_generated_html:
            for u in urls_to_remove:
                f = os.path.join(self.www_path, u)
                log ("removing %s " % f)
                if os.path.exists(f):
                    os.remove(f)


    #
    def parseUrls(self, parse_urls = None):
        """ returns a list of urls parsed from .htaccess.
        """
        urls = []

        with open(os.path.join(self.www_path, '.htaccess')) as afile:
            for line in afile:
                if "RewriteRule" not in line:
                    continue

                parts = line.split(" ")
                if "(.*)" in parts[1][5:]:
                    continue
                url = parts[1].replace('^(.*)', '').replace('$', '')
                if url == '':
                    continue
                urls.append(url)
            return urls


    def generateAllUrls(self, parse_urls = None):
        """ parse_urls - if None, we generate them all.  If False, we generate none of them.
        """
        if parse_urls == "":
            parse_urls = False

        urls = []
        if parse_urls is not False:
            urls += self.parseUrls(parse_urls)
        return urls


    def downloadUrls(self, urls):
        url_data = {}
        for u in urls:
            url = self.base_url + u

            request = urllib.request.Request(url)


            # the .htaccess file checks for the header, and if it exists returns unprocessed data.
            request.add_header('User-agent', 'our-web-crawler')
            try:
                response = urllib.request.urlopen(request)
                data = response.read()
            except urllib.request.HTTPError:
                log (url)
                raise
            except urllib.request.URLError:
                log (url)
                raise
            yield (u,data)

    def process_file(self, old_fname, new_fname):
        """ given the old_fname containing the data, we write the result into the new_fname.
        """

        #../binaries/bin/ssjquery ./ server.json index.html js/libs/jquery-1.6.2.js js/products.js js/yourServerSide.js > renderedHtml.html
        if 0:
            cmd = "cat %s > %s" % (old_fname, new_fname)
            log (cmd)
            os.system(cmd)

        if 1:
            # cmd = "$(npm bin)/ssjquery ./frontend/www server.json %s js/jquery-1.11.0.min.js js/serverSide.js" % (old_fname)
            # cmds = cmd.split()
            # f = open(new_fname, "wb")
            # proc = subprocess.Popen(cmds, stdout = subprocess.PIPE)
            # f.write(proc.communicate()[0])
            # f.close()
            # if proc.returncode != 0:
            #     raise RuntimeError("cmd failed with error :%s:.  cmd:%s:" % (r, cmd))

            cmd = "$(npm bin)/ssjquery ./frontend/www server.json %s js/jquery-1.11.0.min.js js/serverSide.js > %s" % (old_fname, new_fname)
            subprocess.call(cmd, shell=True)



    def generateFiles(self, urls):
        """ generate the files for the given urls.
        """
        # process the data.
        for path, data in self.downloadUrls(urls):
            f = tempfile.NamedTemporaryFile("w", delete=False, dir=self.www_path, prefix= self.temp_prefix)
            f.write(data.decode('utf-8'))
            f.close()
            old_fname = f.name

            f = tempfile.NamedTemporaryFile("w", delete=False, dir=self.www_path, prefix= self.temp_prefix)
            f.close()

            new_fname = f.name

            try:
                self.process_file(os.path.basename(old_fname), new_fname)
                log ("mvim -p %s %s" % (os.path.join(self.www_path, path), old_fname))
                log ((new_fname, os.path.join(self.www_path, path)))
                os.rename(new_fname, os.path.join(self.www_path, path))
                # tmpfile makes weird settings.
                os.chmod(os.path.join(self.www_path, path), 0o644)
            except:
                os.remove(new_fname)
                raise
            finally:
                if self.cleanup_tmp_files_at_end:
                    os.remove(old_fname)




    def compress_javascript(self):
        """ compresses, or minimises the javascript files.
        """

        files = [
            "js/pygame.plugins.js",
            "js/pygame.js",
        ]

        # compress ones that need compressing
        files_to_compress = [f for f in files if ".min.js" not in f]
        files_to_compress = [f for f in files]
        all_compressed_data = []
        for fname in files_to_compress:
            full_fname = os.path.join(self.www_path, fname)
            out_fname = full_fname.replace(".min.js", ".js").replace(".js", ".min.js")
            cmd = ["node_modules/.bin/uglifyjs", full_fname]
            log(cmd)
            # compressed_data = subprocess.check_output(cmd, shell=True)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (compressed_data, _) = proc.communicate()

            all_compressed_data.append(compressed_data)

            with open(out_fname, 'wb') as afile:
                afile.write(compressed_data)
            log('js compression done')

        # concatenate scripts
        #compressed_filenames = [f.replace(".min.js", ".js").replace(".js", ".min.js") for f in files]

        log("concatenate scripts together")

        all_data = b''.join(all_compressed_data)

        out_fname = os.path.join(self.www_path, "js", "pygame.min.js")
        with open(out_fname, 'wb') as afile:
            afile.write(all_data)


    def compress_css(self):
        files = [
            'css/style.css',
            'css/colours.css',
        ]

        files_to_compress = files
        all_compressed_data = []
        for fname in files_to_compress:
            full_fname = os.path.join(self.www_path, fname)
            out_fname = full_fname.replace(".min.css", ".css").replace(".css", ".min.css")
            cmd = ["yuicompressor", full_fname]
            log(cmd)
            try:
                compressed_data = subprocess.check_output(cmd)
            except FileNotFoundError:
                cmd = ["yui-compressor", full_fname]
                log(cmd)
                compressed_data = subprocess.check_output(cmd)

            all_compressed_data.append(compressed_data)

        log("concatenate css together")

        all_data = b''.join(all_compressed_data)

        out_fname = os.path.join(self.www_path, "css", "pygame.min.css")
        with open(out_fname, 'wb') as afile:
            afile.write(all_data)


    @staticmethod
    def parse_args(input_args = None, sys_exit = True):


        # override the argument parser so we can tell it to raise an error or sys.exit.
        class ArgParse(argparse.ArgumentParser):
            def exit(self, status=0, message=None):
                if message:
                    self._print_message(message, argparse._sys.stderr)
                if hasattr(self, "_sys_exit") and not self._sys_exit:
                    raise ValueError(status, message)
                else:
                    argparse._sys.exit(status)

        parser = ArgParse(description='Process some integers.')
        parser._sys_exit = sys_exit

        parser.add_argument('--base_url', default='http://localhost/',
                            help='base url to download from.')
        parser.add_argument('--www_path', default=os.path.join('frontend', 'www'),
                            help='the www directory path')
        parser.add_argument('--json_path', default=os.path.join('frontend', 'www', 'server.json'),
                            help='path to server.json')
        parser.add_argument('--cleanup_tmp_files_at_start', default=True,
                            help='Remove the downloaded tmpfiles.')
        parser.add_argument('--cleanup_tmp_files_at_end', default=True, type=bool,
                            help='Remove the tmpfiles as we go. If False, we leave them ')
        parser.add_argument('--remove_all_html', default=False, action='store_true',
                            help='remove all the .html files first before generating.')
        parser.add_argument('--remove_generated_html', default=False, action='store_true',
                            help='remove .html files we are to generate.')
        parser.add_argument('--log', default=False, action='store_true',
                            help='log stuff.')
        parser.add_argument('--parse_urls', default=None,
                            help='parse urls from .htaccess If None, parse. If False, parse none.')



        parser.add_argument('--minify', default=False, help='minify css or js')


        return parser.parse_args(input_args)

def main():
    args = Urls.parse_args()
    _logit = args.log
    log (args)

    Urls(vars(args))

    # return 0 for a successful run.
    sys.exit(0)

if __name__ == "__main__":
    main()
