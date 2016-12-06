# Package "stundenzettel_generator", Strategy abstract class
# (c) 2015 Sven K., GPL

# Python batteries
import re
from datetime import datetime, timedelta, date
from os import path

# adopt this to your needs
freedays_file = path.join(path.dirname(__file__), 'feier-brueckentage2015.txt')


# abstract class
class Strategy():
    """
	A Strategy for creating a time sheet for a single month. This class should
	hold the method `createSchedule()` for creating such a table.

	The class is constructed with a set of parameters which will be copied as
	object attributes. Thus, any parameter is accessible in a `self.parametername`
	manner. You can also access and check the availability with `'param' in self.data`.

	The Strategy base class contains some helper methods for checking,
	formatting and printing schedules. Schedules are are actually simple lists of
	dictionarys with certain keys which then are used for example in templates for
	usage.
	"""

    defaults = {}

    def __init__(self, data):
        for k, v in self.defaults.iteritems():
            if k in data:
                v = data[k]
            else:
                data[k] = v
            setattr(self, k, v)
        self.data = data

    def read_freedays(self):
        days = []
        with open(freedays_file, 'r') as daylist:
            for line in daylist:
                if re.match(r"^\s*$|^#", line):
                    # skip empty lines and comments
                    continue
                m = re.match(r"^(\d\d)\.(\d\d)\.(\d\d\d\d)", line)
                if m:
                    day, month, year = m.groups()
                    try:
                        days.append(datetime(int(year), int(month), int(day)).date())
                    except Exception as e:
                        print "Bad date '%s' in line '%s'" % (str((day, month, year,)), line)
                        print e
                else:
                    print "Could not parse line '%s'" % line
        return days

    def checkSchedule(self, schedule, silent=True):
        duration = sum([day['working_hours'] for day in schedule])
        all_fine = duration == self.monthly_hours
        if not silent:
            if all_fine:
                print "Schedule checking: All right, have worked %d hours" % duration
            else:
                print "Error: Schedule is wrong, shall work %d hours but worked %d hours." % (
                    self.monthly_hours, duration)
        return all_fine

    def printSchedule(self, schedule):
        """
		Dumps a formatted schedule to stdout. You can use this function as
		`strat.printSchedule(strat.formatSchedule(strat.createSchedule()))`.
		Yes, it should be `strat.createSchedule().format().print()`. But it isn't.
		"""
        # just rerun the formatting to be sure
        schedule = self.formatSchedule(schedule)

        format = "%-10s  %-5s  %-15s  %-5s  %10s %10s"
        keys = tuple(["date", "begin", "pause", "end", "dur", "working_hours"])
        print format % keys
        for day in schedule:
            print format % tuple([str(day[x]) for x in keys])

    def formatSchedule(self, schedule):
        """
		Maps the raw (python object) schedule variables to formatted strings
		"""

        def formatDay(day):
            dmy = lambda key: '{:%d.%m.%Y}'.format(day[key])
            hm = lambda key: '{:%H:%M}'.format(day[key])

            day['date'] = dmy('today')
            day['begin'] = hm('daystart') if day['working_hours'] else '-'
            day['pause'] = '%s-%s' % (hm('break_start'), hm('break_end')) if day['break_hours'] else '-'
            day['end'] = hm('work_end') if day['working_hours'] else '-'
            day['dur'] = str(timedelta(hours=day['working_hours']))
            day['key'] = ''  # no illness, no vacation.
            day['sign'] = ''  # no signature.
            return day

        return map(formatDay, schedule)

    def createSchedule(self):
        raise NotImplementedError("Implement the schedule by deriving a Strategy")
