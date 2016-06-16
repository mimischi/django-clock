# Package "stundenzettel_generator", StundenzettelGenerator main class
# (c) 2015 Sven K., GPL

# package content
from opendocument import OpenDocument
from standupstrategy import StandupStrategy

# python internals
from shutil import copy, rmtree
from os import path, getcwd
import sys


class StundenzettelGenerator:
    """
    The StundenzettelGenerator is an extensible class for organizing the creation
    of a single time sheet.
    """

    def __init__(self, template_filename, target_filename, template_data, logger=None):
        self.template_filename = template_filename
        self.template_dir = path.dirname(template_filename)
        if not self.template_dir:
            self.template_dir = getcwd()
        self.target_filename = target_filename
        self.arg = template_data

        self.working_dir = self.create_working_directory()

        if not logger:
            import logging  # batteries included
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            self.log = logging.getLogger(self.__class__.__name__)
        else:
            self.log = logger

    def create_working_directory(self):
        from tempfile import mkdtemp
        return mkdtemp()

    def copy_template_file(self):
        source = self.template_filename
        target = path.join(self.working_dir, path.basename(source))
        self.log.info("Copying %s -> %s" % (source, target))
        copy(source, target)
        self.working_template = target

    def create_opendocument(self):
        self.doc = OpenDocument(self.working_template, working_dir=self.working_dir)
        return self.doc

    def create_schedule(self):
        # sollte irgendwann mal verschiedene Strategien erlauben
        self.strategy = StandupStrategy(self.arg)
        self.schedule = self.strategy.formatSchedule(self.strategy.createSchedule())
        return self.schedule

    def render_schedule(self):
        if not hasattr(self, 'schedule'):
            self.create_schedule()

        # Set up template data: Lowercase all existing variables
        data = {"var_" + k.lower(): v for k, v in self.arg.iteritems()}

        dayrows = self.schedule
        append_rows = 32 - len(dayrows)
        empty_row = {k: '' for k in ['date', 'begin', 'pause', 'end', 'dur', 'key', 'sign']}
        dayrows += [empty_row] * append_rows
        # and merge the schedule
        for i, day in enumerate(dayrows):
            for key, value in day.iteritems():
                data['%s%d' % (key, i)] = value

        print "data:"
        print data
        self.log.info("Running OpenDocument template")
        self.doc.run_template(data, render_pdf=True)

    def make(self):
        self.copy_template_file()
        self.create_opendocument()

        self.render_schedule()

        self.log.info("Copying PDF to " + self.template_dir)
        copy(self.doc.pdf_filename, self.template_dir)
