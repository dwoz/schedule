from . import dates
import collections
import calendar

__all__ = ['factory', 'once', 'daily', 'weekly', 'monthly', 'yearly']

class SchedulerError(Exception):
    """
    Raised on invalid user input.
    """

    def __init__(self, *msgs):
        self.msgs = list(msgs)

    def __str__(self):
        l = []
        for msg in self.msgs:
            if not isstr(msg) and isinstance(msg, collections.Iterable):
                # Some msgs are lists so can go through translation if desired.
                msg = ''.join(ustr(i) for i in msg)
            l.append(ustr(msg))
        return ' | '.join(l)

    def __len__(self):
        return len(self.msgs)

    def add(self, *msgs):
        for msg in msgs:
            if isinstance(msg, SchedulerError):
                self.msgs.extend(msg)
            else:
                self.msgs.append(msg)

    def add_field(self, name, reason, val=None):
        """
        Provide consistent interface for reporting fields with invalid values.
        """
        l = [name, ' = {0}'.format(ustr(val)), ' : ']
        if isstr(reason):
            l.append(reason)
        else:
            l.extend(reason)
        if val is None or reason in ('empty', 'undefined'):
            # Don't bother showing value if empty or undefined.
            l.pop(1)
        self.add(tuple(l))

    def __iter__(self):
        return self.msgs.__iter__()

DAYS = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')

def factory(start, end=None, repeat='once', interval=1, days=[], weeks={}):
    """
    Return new Schedule instance based on given options.
    """
    errors = SchedulerError()
    if not start:
        errors.add_field('start', 'undefined')
    if repeat not in ('once', 'daily', 'weekly', 'monthly', 'yearly'):
        errors.add_field('repeat', 'unknown', repeat)
    if repeat != 'once' and not interval:
        errors.add_field('interval', 'undefined')
    if repeat in ('weekly', 'monthly', 'yearly') and not days:
        if repeat == 'monthly':
            hasweeks = False
            if weeks:
                weeks = weeks.copy()
                cleanweeks = {1:[], 2:[], 3:[], 4:[], 5:[]}
                for a in weeks:
                    k = int(a)
                    if k not in cleanweeks:
                        errors.add_field('weeks', 'invalid week', k)
                    else:
                        for b in sorted([int(c) for c in weeks[a]]):
                            if b >= 0 and b <= 6:
                                hasweeks = True
                                cleanweeks[k].append(b)
                            else:
                                errors.add_field('weeks', 'invalid day', b)
            if not hasweeks and not days:
                errors.add_field('days', 'undefined')
            else:
                days = sorted([int(a) for a in days])
                for a in days:
                    if a < 1 or a > 31:
                        errors.add_field('days', 'invalid day', a)
        elif repeat == 'weekly':
            if not days:
                errors.add_field('days', 'undefined')
            days = sorted([int(a) for a in days])
            for a in days:
                if a < 0 or a > 6:
                    errors.add_field('days', 'invalid day', a)
    try:
        if repeat == 'once':
            schedule = Once(start)
        elif repeat == 'daily':
            schedule = Daily(start, end, interval) 
        elif repeat == 'weekly':
            schedule = Weekly(days, start, end, interval)
        elif repeat == 'monthly':
            schedule = Monthly(days, start, end, interval, weeks)
        elif repeat == 'yearly':
            schedule = Yearly(days, start, end, interval)
    except SchedulerError as e:
        errors.add(e)
    if errors:
        raise errors
    return schedule

def once(start):
    """
    Return a once-only Schedule instance.
    """
    return factory(start)

def daily(start, end=None, nInterval=1):
    """
    Return a daily Schedule instance.
    """
    return factory(start, end, 'daily', nInterval)

def weekly(lDays, start, end=None, nInterval=1):
    """
    Return a weekly Schedule instance for given days of the week.
    Given days can be one or more from: mon, tue, wed, thu, fri, sat, sun.
    """
    d = dict(mon=0, tue=1, wed=2, thu=3, fri=4, sat=5, sun=6)
    for s in lDays:
        if s not in d:
            raise SchedulerError("Unknown day of week: " + s)
    return factory(start, end, 'weekly', nInterval, [d[i] for i in lDays])

def monthly(lDays, start, end=None, nInterval=1, weeks={}):
    """
    Return a monthly Schedule instance.  Given days can be one or more from: 1-31.
    """
    return factory(start, end, 'monthly', nInterval, lDays, weeks.copy())

def yearly(lDays, start, end=None, nInterval=1):
    """
    Return a yearly Schedule instance.  Given days can be one or more from 1-366.
    """
    return factory(start, end, 'yearly', nInterval, lDays)


class Schedule(object):
    """
    Interface for Schedule types to implement.

    Given a schedule with steps ts1, ts2, and ts3
    where ts1 < ts2 and ts2 < ts3:

      * [ts1, ts2) is the last step range for ts1
      * (ts2, ts3] is the next step range for ts2

    In other words, if a given timestamp (ts) falls exactly on a
    schedule's step, then the last step is that step and the next
    step, well, the next step.
    """

    def prev_step(self, ts=None):
        """
        Return last datetime instance for this schedule relative to
        given timestamp (defaults to now).  If there is no logical
        last step (eg one-time schedule where start > ts), then None
        is returned.
        """
        if not ts:
            ts = dates.now()
        interval = self.get_interval(ts)
        ts_period = self.start_of_period(ts)
        ts_day = self.period_day(ts)
        # When looking for the last step, roll back a day
        # if the ts time of day is to early for a step.
        if ts.time() <= self.start.time():
            #back up one day.
            ts_day -= 1
        # The ts_period is always greater than or equal to the
        # interval. If the ts_period is greater than the interval
        # then the step we are looking for is the last step
        # of the interval.
        if interval < ts_period:
            step_day = dates.delta(interval, nDays=self._offset(self.days(ts)[-1]))
        else:
            # The ts period is equal to the first period
            # of the interval.
            if ts_day < self.days(ts)[0]:
                # Last day of previous interval
                interval = self.last_interval(ts)
                step_day = dates.delta(interval, nDays=self._offset(self.days(ts)[-1]))
            elif ts_day >= self.days(ts)[-1]:
                # Last step of this interval
                step_day = dates.delta(interval, nDays=self._offset(self.days(ts)[-1]))
            else:
                # The ts day is greater than or equal to the first step
                # but less than the last step. Walk backwards through 
                # the steps until we find the first one that is less
                # than or equal to the ts day.
                for d in sorted(self.days(ts), reverse=True):
                    if d <= ts_day:
                        break
                step_day = dates.delta(interval, nDays=self._offset(d))
        prev_step = dates.date.combine(step_day.date(), self.start.time())
        if prev_step < self.start:
            return None
        if self.end and prev_step > self.end:
            # If we are asking for the last step semetime after
            # the end of a schedule, use the end date to find.
            # the schduled true last step.
            return self.prev_step(dates.delta(self.end, nSecs=1))
        return prev_step

    def next_step(self, ts=None):
        """
        Return next datetime instance for this schedule relative to
        given timestamp (defaults to now).  If there is no logical
        next step (eg one-time schedule where start < ts), then None
        is returned.
        """
        if not ts:
            ts = dates.now()
        interval = self.get_interval(ts)
        ts_period = self.start_of_period(ts)
        ts_day = self.period_day(ts)
        # When looking for the next step roll forward if the ts
        # time of day is to late for a step.
        if ts.time() >= self.start.time():
            ts_day += 1
        # The ts_period is always greater or equal to the interval.
        # if the ts period is greater than the interval it means
        # there the step we are looking for is the first step
        # of the next interval.
        if interval < ts_period:
            interval = self.next_interval(ts)
            step_day = dates.delta(interval, nDays=self._offset(self.days(ts)[0]))
        else:
            # The ts period is in the zone.
            if ts_day > self.days(ts)[-1]:
                # The ts day is after all the steps in the interval.
                interval = self.next_interval(ts)
                step_day = dates.delta(interval, nDays=self._offset(self.days(ts)[0]))
            elif ts_day <= self.days(ts)[0]:
                # The ts day is before all the steps in the interval.
                step_day = dates.delta(interval, nDays=self._offset(self.days(ts)[0]))
            else:
                # The ts day is less than or equal to the last step
                # and greater than the first step. Walk forward through
                # the steps until we find one that is greater than
                # or equal to the ts day.
                for d in self.days(ts):
                    if ts_day <= d:
                        break
                step_day = dates.delta(interval, nDays=self._offset(d))
        next_step = dates.date.combine(step_day.date(), self.start.time())
        if self.end and next_step > self.end:
            return None
        if next_step < self.start:
            # If we are asking for the first step before the start of the
            # scehdule, use the start date to find the actual first step.
            return self.next_step(dates.delta(self.start, nSecs=-1))
        return next_step

    def first_step(self):
        return self.next_step(dates.delta(self.start, nSecs=-1)

    def last_step(self):
        return self.prev_step(dates.delta(self.end, nSecs=1)) if self.end else None

    def steps(self, after=None, before=None):
        """
        Iterate over all the steps in a given timeframe.
        If before or after is ommited assume the schedule's
        start and end date.
        """
        if not after:
            after = dates.delta(self.start, nSecs=-1)
        if not before:
            if self.end:
                before = dates.delta(self.end, nSecs=1)
            else:
                before = dates.delta(self.start, nMonths=3)
        step = after
        while True:
            step = self.next_step(step)
            if step and step <= before:
                yield step
            else:
                raise StopIteration

    def days(self, ts=None):
        return self.lDays

    def _offset(self, day):
        """
        Schedules who's first day is an 1 and not a 0 will
        require an offset.
        """
        if hasattr(self, 'offset'):
            return self.offset(day)
        return day

    # Each Schedule type must implement the following methods. Some
    # Schedules will also implement an 'offset' method.

    def summary(self, fmt='%Y-%m-%d'):
        """
        Return summary of this schedule.  Return value is a list of
        strings so can play nice with localization.
        """
        raise Exception('Interface method undefined.')

    def get_interval(self, ts):
        """
        Return the begining of the interval ts in apart of.
        An interval is made up of one or more periods. For
        example, For a daily schedule where the interval is
        set to two, each interval is made up of two 'one day'
        periods.
        """
        raise Exception('Interface method undefined.')

    def period_day(self, ts):
        "Return the timstamp's period day."
        raise Exception('Interface method undefined.')

    def start_of_period(self, ts):
        "Return the begining of the period for ts is in."
        raise Exception('Interface method undefined.')

    def next_interval(self, ts):
        "The interval before the one ts is apart of."
        raise Exception('Interface method undefined.')

    def last_interval(self, ts):
        "The interval before the one ts in apart of."
        raise Exception('Interface method undefined.')


class Once(Schedule):

    def __init__(self, start):
        self.sType = 'once'
        self.start = start
        self.end = start
        self.nInterval = 1
        self.lDays = [0]

    def summary(self, fmt='%Y-%m-%d'):
        return (("once on {0}", self.start.strftime(fmt)),)

    def get_interval(self, ts):
        """
        Return the begining of the interval ts in apart of.
        A one time schedule's interval will always be the start
        of the ts day.
        """
        return dates.truncate(ts, 'day')

    def start_of_period(self, ts):
        "A one time schedule's period is a day."
        return dates.truncate(ts, 'day')

    def period_day(self, ts):
        """
        One time schedules don't have intervals, or step
        days period day is always 0.
        """
        return 0

    def next_interval(self, ts):
        "The interval before the one ts is apart of."
        interval = self.get_interval(ts)
        return dates.delta(interval, nDays=self.nInterval)

    def last_interval(self, ts):
        "The interval before the one ts in apart of."
        interval = self.get_interval(ts)
        return dates.delta(interval, nDays=-self.nInterval)

class Daily(Schedule):
    """
    Daily Schedule
    """

    def __init__(self, start, end=None, nInterval=1):
        """
        Accepts a start date as well as an optional end date and interval
        """
        self.sType = 'daily'
        self.start = start
        self.end = end
        self.nInterval = nInterval
        self.lDays = [0]

    def summary(self, fmt='%Y-%m-%d'):
        lTxt = []
        if self.nInterval == 1:
            lTxt.extend(('every day', ' '))
        else:
            lTxt.extend((("every {0} days", self.nInterval), ' '))
        if self.end:
            lTxt.append(("from {0} to {1}", self.start.strftime(fmt), self.end.strftime(fmt)))
        else:
            lTxt.append(("from {0} to forever", self.start.strftime(fmt)))
        return tuple(lTxt)

    def start_of_period(self, ts):
        return dates.truncate(ts, 'day')

    def period_day(self, ts):
        # Daily scheudules don't have lDays
        return 0

    def get_interval(self, ts):
        """
        Return begining of the interval that ts is in.
        """
        start_period = self.start_of_period(self.start)
        ts_period = self.start_of_period(ts)
        dlt = (ts_period - start_period).days
        mod = dlt % self.nInterval
        return dates.delta(start_period, nDays = (dlt - mod))

    def next_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nDays=self.nInterval)

    def last_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nDays=-self.nInterval)

class Weekly(Schedule):
    """
    Weekly Schedule
    """

    def __init__(self, lDays, start, end=None, nInterval=1):
        if not start:
            raise DnaError('Must have a start date.')
        for i in lDays:
            if i < 0 or i > 6:
                raise DnaError("Days of week must be in (0..6): {0}.".format(i))
        self.sType = 'weekly'
        self.lDays = sorted(lDays)
        self.start = start
        self.end = end
        self.interval = nInterval

    def summary(self, fmt='%Y-%m-%d'):
        lTxt = []
        if self.interval != 1:
            lTxt.extend((("every {0} weeks", self.interval), ' '))
        else:
            lTxt.extend(('every week', ' '))
        lTxt.extend(('on [days]', ' '))

        if len(self.lDays) > 1:
            for n in self.lDays[:-1]:
                lTxt.extend((DAYS[n], ' '))
            lTxt.extend(('&', ' ', DAYS[self.lDays[-1]], ' '))
        else:
            lTxt.extend((DAYS[self.lDays[-1]], ' '))
        if self.end:
            lTxt.append(("from {0} to {1}", self.start.strftime(fmt), self.end.strftime(fmt)))
        else:
            lTxt.append(("from {0} to forever", self.start.strftime(fmt)))
        return tuple(lTxt)

    def period_day(self, ts):
        return ts.weekday()

    def start_of_period(self, ts):
        return dates.truncate(ts, 'week')

    def get_interval(self, ts):
        start_period = self.start_of_period(self.start)
        ts_period = self.start_of_period(ts)
        dlt = (ts_period - start_period).days / 7
        nMod = dlt % self.interval
        return dates.delta(start_period, nDays = 7 * (dlt - nMod))

    def last_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nDays = -(7 * self.interval))

    def next_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nDays = (7 * self.interval))

class Monthly(Schedule):
    """
    Monthly Schedule
    """

    def __init__(self, lDays, start, end=None, nInterval=1, weeks={}):
        if not start:
            raise DnaError('Must have a start date.')
        if not nInterval:
            raise DnaError("Interval must be > 0 for recurring schedules: {0}.".format(nInterval))
        for i in lDays:
            if i < 1 or i > 31:
                raise DnaError("Days of month must be in (1..31): {0}.".format(i))
        self.sType = 'monthly'
        self.start = start
        self.end = end
        self.interval = nInterval
        self.lDays = sorted(lDays)
        self.weeks = {1: [], 2: [], 3: [], 4: [], 5:[]}
        for a in weeks:
            self.weeks[int(a)] = sorted([int(b) for b in weeks[a]])

    def summary(self, fmt='%Y-%m-%d'):
        lTxt = []
        if self.interval != 1:
            lTxt.extend((("every {0} months", self.interval), ' '))
        else:
            lTxt.extend(('every month', ' '))
        lTxt.extend(('on [days]', ' '))
        if len(self.lDays) > 1:
            for n in self.lDays[:-1]:
                lTxt.extend((str(n), ' '))
            lTxt.extend(('&', ' ', str(self.lDays[-1]), ' '))
        elif self.lDays:
            lTxt.extend((str(self.lDays[-1]), ' '))
        types = ('first', 'second', 'third', 'fourth', 'last',)
        for a, b in enumerate(types):
            if self.weeks[a + 1]:
                l = [b, ' ']
                for c in self.weeks[a + 1]:
                    l.extend([DAYS[c], ' '])
                lTxt.extend(l)
        if self.end:
            lTxt.append(("from {0} to {1}", self.start.strftime(fmt), self.end.strftime(fmt)))
        else:
            lTxt.append(("from {0} to forever", self.start.strftime(fmt)))
        return tuple(lTxt)

    def period_day(self, ts):
        return ts.day

    def start_of_period(self, ts):
        return dates.truncate(ts, 'month')

    def offset(self, day):
        return day - 1

    def get_interval(self, ts):
        start_period = self.start_of_period(self.start)
        ts_period = self.start_of_period(ts)
        delta_years = ts_period.year - start_period.year
        delta_months = ts_period.month - start_period.month
        dlt = (delta_years * 12) + delta_months
        nMod = dlt % self.interval
        return dates.delta(start_period, nMonths = (dlt - nMod))

    def last_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nMonths = -self.interval)

    def next_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nMonths = self.interval)

    def days(self, ts=None):
        """
        Determine the days this schedule will run in a given month.

        A montly schedule can be scheduled by day of month or by the week and
        weekday. When scheduling by week and weekday the weeks attribute is
        used to determine what days in the schedule will run. Keys 1,2,3, and 4
        of the weeks attribute represent the first, second, third and fourth
        occurance of the weekdays the key maps to. For example {1:[0]} is the
        first Monday of a month and {4:[6]} is the fourth Sunday of a month.
        Key 5 represents the last week of a month. For example {5:[0]}
        represents the last Monday of a month.
        """
        days = set(self.lDays)
        if not self.weeks:
            return sorted(list(days))
        ts = ts or dates.now()
        # First day of first week and number of days in month
        sdow, mdays = calendar.monthrange(ts.year, ts.month)
        dow = sdow
        week = 0
        startlastweek = mdays - 6
        for dom in range(1, mdays + 1):
            if dow == sdow:
                week += 1
            if week != 5 and week in self.weeks and dow in self.weeks[week]:
                days.add(dom)
            if dom >= startlastweek and 5 in self.weeks and dow in self.weeks[5]:
                days.add(dom)
            if dow == 6:
                dow = 0
            else:
                dow += 1
        return sorted(list(days))


class Yearly(Schedule):
    """
    Yearly Schedule
    """

    def __init__(self, lDays, start, end=None, nInterval=1):
        if not start or not lDays:
            raise DnaError('Must have a start date.')
        for i in lDays:
            if i < 1 or i > 366:
                raise DnaError("Days of year must be in (1..366): {0}.".format(i))
        self.sType = 'yearly'
        self.start = start
        self.end = end
        self.nInterval = nInterval
        self.lDays = sorted(lDays)

    def summary(self, fmt='%Y-%m-%d'):
        """
        Return textual summary of this schedule.
        """
        lTxt = []
        if self.nInterval != 1:
            lTxt.extend((("every {0} years", self.nInterval), ' '))
        else:
            lTxt.extend(('every year', ' '))
        lTxt.extend(('on [days]', ' '))
        if len(self.lDays) > 1:
            for n in self.lDays[:-1]:
                lTxt.extend((str(n), ' '))
            lTxt.extend(('&', ' ', str(self.lDays[-1]), ' '))
        else:
            lTxt.extend((str(self.lDays[-1]), ' '))
        if self.end:
            lTxt.append(("from {0} to {1}", self.start.strftime(fmt), self.end.strftime(fmt)))
        else:
            lTxt.append(("from {0} to forever", self.start.strftime(fmt)))
        return tuple(lTxt)

    def period_day(self, ts):
        ts = ts.timetuple()
        return ts.tm_yday

    def start_of_period(self, ts):
        return dates.truncate(ts, 'year')

    def offset(self, day):
        return day - 1

    def get_interval(self, ts):
        if not ts:
            ts = dates.now()
        start_period = self.start_of_period(self.start)
        ts_period = self.start_of_period(ts)
        dlt = ts_period.year - start_period.year
        nMod = dlt % self.nInterval
        return dates.delta(start_period, nYears = (dlt - nMod))

    def last_interval(self, ts):
        interval = self.get_interval(ts)
        return dates.delta(interval, nYears = - self.nInterval)

    def next_interval(self, ts=None):
        interval = self.get_interval(ts)
        return dates.delta(interval, nYears = self.nInterval)
