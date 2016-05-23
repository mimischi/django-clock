# Package "stundenzettel_generator", Strategy abstract class
# (c) 2015 Sven K., GPL

from strategy import Strategy

# Python batteries
import re
import calendar
import random
from datetime import datetime, timedelta, date as objdate
from math import sqrt, pi, exp


# helper functions
def is_weekday(year, month, day):
    try:
        weekday = calendar.weekday(year, month, day)
    except ValueError:
        # filters also out days like 32.10.2015
        return False
    return weekday < calendar.SATURDAY


def random_bool():
    return bool(random.getrandbits(1))


# weighted random
def likely_true(probab=0.5):
    l = [True] * int(probab * 100) + [False] * int((1 - probab) * 100)
    return random.choice(l)


def round_to_half(number):
    return round(number * 2) / 2


class StandupStrategy(Strategy):
    """
    The StandupStrategy is one simple Strategy. It works by guessing numbers according
    to Gaussian distributions and tresholds on a day by day basis.

    The algorithm works as follows:

       * Determine the average daily working hours
       * For each day: Guess the starting time, actual working hours, need for a break,
         determine end time.
       * Whenever given constraints are not met and corrections are nontrivial, just
         restart creating the day or month. Typically this scales well: Roughly every
         10th day or month has to be done twice.

    Note that some parameters are quite sensitive or dependent on each other. This is
    expressed in comments in the lines.
    """

    defaults = {
        # guiding principles and basically open parameters:
        'month': 10,
        'year': 2015,
        'monthly_hours': 40,

        # detailed parameters which probably should not be touched
        # if you don't know what you do
        'daystart_min': 8,
        'daystart_max': 16,
        'daystart_probab_athalf': 0.35,
        'avg_dayhours_sigma': 3,
        'do_break_treshold': 3,
        'daily_min_worktime': 2,  # must be bigger than 0 (zero)
        'daily_max_worktime': 8,  # should be smaller equal 24
        'daily_latest_end_hour': 22,  # should be >daystart_max and <=24
        'break_hours_avg': 1,  # longer breaks makes more iterations neccessary
        'break_hours_sigma': .5,
        'break_hours_min': .5,
        'break_rel_ratio': .4,  # means that after 4/10 of daily working time, the break is made
        'break_rel_ratio_sigma': .2,
        'break_min_hours_before': .5,  # must be smaller than daily_min_worktime

        # keep empty working days or not. Presumably not.
        'keep_empty_days': False,
    }

    # measure performance
    dayit = 0
    monthit = 0

    def recreateDay(self, day):
        self.dayit += 1
        return self.createDay(day)

    def recreateMonth(self):
        self.monthit += 1
        return self.createMonth()

    def createDay(self, day):
        month, year = self.month, self.year
        today = datetime(year, month, day)

        daystart_range = range(self.daystart_min, self.daystart_max)
        daystart_hour = random.choice(daystart_range)

        if likely_true(self.daystart_probab_athalf):
            daystart_hour += 0.5

        daystart = today + timedelta(hours=daystart_hour)
        # print "Starting at "+str(daystart)

        # apply a gaussian on the daily working hours
        working_hours = round_to_half(random.gauss(self.avg_dayhours, self.avg_dayhours_sigma))

        # check some treshholds and the remaining work time
        if working_hours > self.daily_max_worktime:
            working_hours = self.daily_max_worktime
        if working_hours < self.daily_min_worktime:
            working_hours = 0
        if self.remaining_hours <= working_hours:
            working_hours = self.remaining_hours

        # work this time today. Do not yet store globally: If the creation
        # fails, we can safely restart the day creation
        remaining_hours = self.remaining_hours - working_hours

        if day == self.last_day and remaining_hours > 0:
            # work off the month today. Presumably this does not
            # yield in extremely long working sessions.
            working_hours = remaining_hours

        # make a break if the working time is too long
        break_hours = 0
        if working_hours >= self.do_break_treshold:
            break_hours = round_to_half(random.gauss(self.break_hours_avg, self.break_hours_sigma))
            if break_hours < self.break_hours_min:
                break_hours = 0

        while break_hours:
            hours_work_before_break = round_to_half(random.gauss(
                working_hours * self.break_rel_ratio,
                working_hours * self.break_rel_ratio_sigma))

            if hours_work_before_break < self.break_min_hours_before:
                continue  # find a new working time before break

            break_start = daystart + timedelta(hours=hours_work_before_break)
            break_end = break_start + timedelta(hours=break_hours)
            # print "Breaking from %s to %s" % (str(break_start), str(break_end))
            break
        else:
            break_start = break_end = None

        # make sure we end work before bed time
        work_end = daystart + timedelta(hours=working_hours + break_hours)
        latest_end = daystart + timedelta(hours=self.daily_latest_end_hour)

        if work_end > latest_end:
            return self.recreateDay(day)  # find a new working time configuration

        # finalize the day, write out the globals and return something
        today_results = {}
        self.remaining_hours = remaining_hours

        if working_hours > 0 or self.keep_empty_days:
            # pack the results
            for i in ('today', 'daystart', 'break_start', 'break_hours', 'break_end', 'work_end', 'working_hours',
                      'remaining_hours'):
                today_results[i] = locals()[i]

        return today_results

    def createMonth(self):
        recreateMonth = lambda: self.createMonth()
        # reset global remaining hours
        self.remaining_hours = self.monthly_hours
        results = []

        for day in self.weekdays:
            day_results = self.createDay(day)

            if day_results:
                results.append(day_results)

                # print "Created month: "
                # from pprint import pprint; pprint(results)

        # if month does not pass tests, recursively redo the month
        return results if self.checkSchedule(results) else self.recreateMonth()

    def createSchedule(self, format_output=False):
        month, year = self.month, self.year

        calendar.setfirstweekday(calendar.MONDAY)
        self.weekdays = [day for day in range(1, 32) if is_weekday(year, month, day)]

        # filter out all holidays or bridging days
        holidays = self.read_freedays()
        self.weekdays = [day for day in self.weekdays if not objdate(year, month, day) in holidays]

        num_days = len(self.weekdays)

        # "global variables" during the run
        self.avg_dayhours = float(self.monthly_hours) / num_days
        self.last_day = self.weekdays[-1]

        print "This is StandupStrategy with %d hours in month %d-%d (%d working days, %f hours/day)" % (
        self.monthly_hours, month, year, num_days, self.avg_dayhours)
        results = self.createMonth()
        print "Performance: %d day reiterations, %d month reiterations" % (self.dayit, self.monthit)
        return results if not format_output else self.formatSchedule(results)


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description='Testing the StandupStrategy algorithm')
    parser.add_argument('--iterations', metavar='N', dest='iterations', type=int, default=1,
                        help='How many iterations you want to run')
    parser.add_argument('--month', metavar='MM', dest='month', type=int, choices=range(1, 12),
                        help='Month as number (2 digits)')
    parser.add_argument('--year', metavar='YYYY', dest='year', type=int, choices=range(1970, 2020),
                        help='Year as number (4 digits)')

    args = parser.parse_args()
    if not args.month or not args.year:
        print "Missing month or year"
        parser.print_usage()
        sys.exit(1)

    # example data
    data = {'month': args.month, 'year': args.year}

    s = StandupStrategy(data)

    for i in range(0, args.iterations):
        res = s.createSchedule()
        s.checkSchedule(res, silent=False)
        s.printSchedule(res)
