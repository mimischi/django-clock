# package "stundenzettel_generator"
# a class with some handy manipulation functions

# requirements: lxml for python*2* (install e.g.: pip install lxml)
from lxml import etree

# batteries
import os
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from os import path
import subprocess
from subprocess import call
import re


class OpenDocument:
    def __init__(self, opendoc_filename, working_dir='./'):
        self.opendoc_filename = opendoc_filename
        self.pdf_filename = path.splitext(self.opendoc_filename)[0] + '.pdf'
        self.working_dir = working_dir

    def extract(self, filename='content.xml'):
        # extract content
        with ZipFile(self.opendoc_filename, mode='r') as z:
            z.extract(filename, path=self.working_dir)
        self.content_fname = path.join(self.working_dir, 'content.xml')
        print "Extracted %s" % self.content_fname

    def update(self, new_content_string, filename='content.xml'):
        filename = path.join(self.working_dir, filename)
        print "Writing out changes to %s" % filename
        with open(filename, 'w') as content_file:
            content_file.write(new_content_string.decode('utf-8'))
        updateZip(self.opendoc_filename, 'content.xml', new_content_string)
        print "Finished patching the OpenDocument file"

    def renderpdf(self):
        # now render that file to PDF using libreoffice
        print "Calling soffice to generate PDF from %s => %s" % (self.opendoc_filename, self.pdf_filename)
        ret = call(
            ['soffice', '--headless', '--convert-to', 'pdf', '--outdir', self.working_dir, self.opendoc_filename],
            stderr=subprocess.STDOUT)
        print "Created PDF successfully" if ret == 0 else "Return value is %i. This is probably an error." % ret

    def apply_template(self, data):
        if not self.content_fname:
            print "Call extract() before"
            return

        content_etree = etree.parse(self.content_fname)
        root = content_etree.getroot()

        # find all templates of the form $IDENTIFIER
        nodes = root.xpath("//*[contains(., '$')]", namespaces=root.nsmap)
        # filter out all without text
        nodes = filter(lambda e: e.text != None, nodes)

        def repl(m):
            varname = m.group(1).lower()
            r = data[varname] if varname in data else '%s NOT FOUND' % varname
            # print "%s -> %s" % (varname, r)
            #
            # Decode everything as unicode. This step is neccessary if raw numbers are
            # given as template data. If your python string (str(2) oder "this") contains
            # special characters, make sure you encode them or use u"german stuff".
            return unicode(r)

        # now replace the templates
        for e in nodes:
            e.text = re.sub(r'\$([A-Z_0-9]+)', repl, e.text)

        print "Fertig mit Ersetzen"
        return etree.tostring(root, pretty_print=True)

    def run_template(self, data, render_pdf=False):
        if not hasattr(self, 'content_fname'):
            self.extract()
        new_text = self.apply_template(data)
        self.update(new_text)
        if render_pdf:
            self.renderpdf()


# a helper function for updating a zip file
# http://stackoverflow.com/questions/25738523/how-to-update-one-file-inside-zip-file-using-python

def updateZip(zipname, filename, data):
    # generate a temp file
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)

    # create a temp copy of the archive without filename
    with ZipFile(zipname, 'r') as zin:
        with ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment  # preserve the comment
            for item in zin.infolist():
                if item.filename != filename:
                    zout.writestr(item, zin.read(item.filename))

    # replace with the temp archive
    os.remove(zipname)
    os.rename(tmpname, zipname)

    # now add filename with its new data
    with ZipFile(zipname, mode='a', compression=ZIP_DEFLATED) as zf:
        zf.writestr(filename, data)
