"""
Automated tests for the scheduling library.
"""

from .. import dates, schedule
from . import test

def translate(lPhrases):
    l = []
    for phrase in lPhrases:
        if isinstance(phrase, str):
            l.append(phrase)
        else:
            l.append(phrase[0].format(*phrase[1:]))
    return ''.join(l)


@test.equals('every day from 2010-01-01 to 2011-01-01')
def daily1():
    'Scheduled every day for a year.'
    s = schedule.daily(dates.date(2010, 1, 1), dates.date(2011, 1,1 ))
    return translate(s.summary())

@test.equals('every 2 days from 2010-01-01 to forever')
def daily2():
    'Scheduled every other day forever.'
    s = schedule.daily(dates.date(2010, 1, 1), nInterval=2)
    return translate(s.summary())

@test.equals('every week on [days] monday & sunday from 2010-01-01 to forever')
def weekly1():
    'Scheduled every Monday & Sunday forever.'
    s = schedule.weekly(('mon', 'sun'), dates.date(2010, 1, 1))
    return translate(s.summary())

@test.equals('every week on [days] monday wednesday & friday from 2010-01-01 to forever')
def weekly2():
    'Scheduled every other Mon, Wed, & Fri forever.'
    s = schedule.weekly(('mon', 'wed', 'fri'), dates.date(2010, 1, 1))
    return translate(s.summary())

@test.equals('every 4 weeks on [days] sunday from 01.01.2010 to forever')
def weekly3():
    'Scheduled every 4th other Sun.'
    s = schedule.weekly(('sun',), dates.date(2010, 1, 1), nInterval=4)
    return translate(s.summary('%d.%m.%Y'))

@test.raises(schedule.SchedulerError)
def weekly4():
    'Day of week must be mon-sun'
    schedule.weekly(('sun', 'monday'), dates.date(2010, 1, 1))

@test.equals('every month on [days] 3 9 & 21 from 2010-01-01 to forever')
def monthly1():
    'Scheduled every month on the 9th, 3rd, & 21st.'
    s = schedule.monthly((3, 21, 9), dates.date(2010, 1, 1))
    return translate(s.summary())

@test.equals('every 3 months on [days] 31 from 2010-01-01 to forever')
def monthly2():
    'Scheduled every quarter on the 31st.'
    s = schedule.monthly((31,), dates.date(2010, 1, 1), nInterval=3)
    return translate(s.summary())

@test.raises(DnaError)
def monthly3():
    'Day of month must be in range(1..31).'
    schedule.monthly((33,), dates.date(2010, 1, 1))

@test.equals('every year on [days] 1 99 & 321 from 2010-01-01 to forever')
def yearly1():
    'Scheduled every year on the 1st, 99th, & 321st days.'
    s = schedule.yearly((99, 1, 321), dates.date(2010, 1, 1))
    return translate(s.summary())

@test.raises(DnaError)
def yearly2():
    'Day of year must be in range(1..366).'
    schedule.yearly((33,0), dates.date(2010, 1, 1))

@test.equals(dates.date(2011, 1, 1))
def schedule_once1():
    "Once.last() returns.prev_step scan."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 2, 1)
    return schedule.once(d1).prev_step(d2)

@test.equals(None)
def schedule_once2():
    "Once.last() before scheduled start is none."
    d1 = dates.date(2011, 1, 2, 00, 00, 00)
    d2 = dates.date(2011, 1, 1, 23, 59, 59)
    return schedule.once(d1).prev_step(d2)

@test.equals(None)
def schedule_once3():
    "Once.next() after schedueled is none."
    d1 = dates.date(2011, 1, 1, 1)
    d2 = dates.date(2011, 1, 1, 1)
    return schedule.once(d1).next_step(d2)

@test.equals(dates.date(2011, 1, 2, 00, 00, 00))
def schedule_once4():
    "Once.next() just before scheduled."
    d1 = dates.date(2011, 1, 2, 00, 00, 00)
    d2 = dates.date(2011, 1, 1, 23, 59, 59)
    return schedule.once(d1).next_step(d2)

@test.equals((('once on {0}', '2011-01-02'),))
def schedule_once5():
    "Once.summary() is translatable."
    d1 = dates.date(2011, 1, 2, 00, 00, 00)
    return schedule.once(d1).summary()

@test.equals(None)
def schedule_daily1():
    "Daily.last() before schdueld is none."
    d1 = dates.date(2011, 1, 2, 00, 00, 00)
    d2 = dates.date(2011, 1, 1, 23, 59, 59)
    return schedule.daily(d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 1, 1, 1, 1))
def schedule_daily2():
    "Daily.last() just after scheduled is scheduled."
    d1 = dates.date(2011, 1, 1, 1, 1, 1)
    d2 = dates.date(2011, 1, 1, 1, 1, 2)
    return schedule.daily(d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 1))
def schedule_daily3():
    "Daily.last() on everyday schedule's first recurrence."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 2)
    return schedule.daily(d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 2, 12, 12))
def schedule_daily_next_3():
    "Daily.next() after everyday schedule's first recurrence."
    d1 = dates.date(2011, 1, 1, 12, 12)
    d2 = dates.date(2011, 1, 2, 00, 00)
    return schedule.daily(d1).next_step(d2)

@test.equals(dates.date(2011, 1, 2))
def schedule_daily4():
    "Daily.last() after end date."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 2)
    d3 = dates.date(2011, 1, 3)
    return schedule.daily(d1, end = d2).prev_step(d3)

@test.equals(dates.date(2011, 1, 1))
def schedule_daily5():
    "Daily.last() after every other day schedule's day 1."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 2)
    return schedule.daily(d1, nInterval = 2).prev_step(d2)

@test.equals(dates.date(2011, 1, 5))
def schedule_daily6():
    "Daily.next() 3 days after every other day schedule's day 1."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 4)
    return schedule.daily(d1, nInterval = 2).next_step(d2)

@test.equals(dates.date(2011, 1, 4))
def schedule_daily7():
    "Daily.last() 5 days after every three days schedule's day 1."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 6)
    return schedule.daily(d1, nInterval = 3).prev_step(d2)

@test.equals(dates.date(2011, 1, 13))
def schedule_daily8a():
    "Daily.next() 9 days after every three days schedule's day 1."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 10)
    return schedule.daily(d1, nInterval = 3).next_step(d2)

@test.equals(dates.date(2011, 1, 13, 13, 10))
def schedule_daily8b():
    "Daily.next() almost 10 days after every three days schedule's day 1 (hours preserved)."
    d1 = dates.date(2011, 1, 1, 13, 10, 00)
    d2 = dates.date(2011, 1, 11, 00, 00, 00)
    return schedule.daily(d1, nInterval = 3).next_step(d2)

@test.equals(dates.date(2011, 1, 19))
def schedule_daily9a():
    "Daily.last() at end date."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 20)
    return schedule.daily(d1, end = d2, nInterval = 3).prev_step(d2)

@test.equals(dates.date(2011, 1, 19, 12, 10))
def schedule_daily9b():
    "Daily.last() at end date (hours preserved)."
    d1 = dates.date(2011, 1, 1, 12, 10, 00)
    d2 = dates.date(2011, 1, 20, 00, 00, 00)
    return schedule.daily(d1, end = d2, nInterval = 3).prev_step(d2)

@test.equals(None)
def schedule_daily10():
    "Daily.next() after end date."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 21)
    return schedule.daily(d1, end = d2, nInterval = 3).next_step(d2)

@test.equals(dates.date(2011, 1, 2))
def schedule_daily11():
    "Daily.next() at the beginning."
    d1 = dates.date(2011, 1, 1)
    return schedule.daily(d1).next_step(d1)

@test.equals(dates.date(2012, 3, 3, 12, 0, 0, 0))
def schedule_daily12():
    'Daily schedule every day'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    return sch.next_step(start)

@test.equals(dates.date(2012, 3, 2, 12, 0, 0, 0))
def schedule_daily13():
    'Daily last one sec after first step yields first step'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    return sch.prev_step(dates.delta(start, nSecs=1))


@test.equals(dates.date(2012, 3, 2, 12, 0, 0, 0))
def schedule_daily14():
    'Daily next on sec before first step yields first step.'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    return sch.next_step(dates.delta(start, nSecs=-1))

@test.equals(dates.date(2012, 3, 2, 12, 0, 0, 0))
def schedule_daily15():
    'Daily last on second step yeild first step.'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    tomorrow = dates.delta(start, nDays=1)
    return sch.prev_step(tomorrow)

@test.equals(dates.date(2012, 3, 4, 12, 0, 0, 0))
def schedule_daily16():
    'Daily next on second step yeild third step.'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    tomorrow = dates.delta(start, nDays=1)
    return sch.next_step(tomorrow)

@test.equals(dates.date(2012, 3, 3, 12, 0, 0, 0))
def schedule_daily17():
    'Daily last one sec after second step.'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    tomorrow = dates.delta(start, nDays=1)
    return sch.prev_step(dates.delta(tomorrow, nSecs=1))

@test.equals(dates.date(2012, 3, 3, 12, 0, 0, 0))
def schedule_daily18():
    'Daily next one sec before second step.'
    start = dates.date(2012, 3, 2, 12, 0, 0, 0)
    sch = schedule.daily(start, nInterval=1)
    tomorrow = dates.delta(start, nDays=1)
    return sch.next_step(dates.delta(tomorrow, nSecs=-1))

@test.equals(None)
def schedule_weekly1():
    "Weekly.last() before first recurrence is none."
    d1 = dates.date(2011, 1, 3)
    d2 = dates.date(2011, 1, 4)
    return schedule.weekly(('thu', 'sun'), d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 6))
def schedule_weekly2():
    "Weekly.next() before first recurrence is first recurrence."
    d1 = dates.date(2011, 1, 3)
    d2 = dates.date(2011, 1, 4)
    return schedule.weekly(('thu', 'sun'), d1).next_step(d2)

@test.equals(dates.date(2011, 1, 6, 12, 10))
def schedule_weekly_next_2():
    "Weekly.next() before first recurrence is first recurrence."
    d1 = dates.date(2011, 1, 3, 12, 10, 00)
    d2 = dates.date(2011, 1, 4, 00, 00, 00)
    return schedule.weekly(('thu', 'sun'), d1).next_step(d2)

@test.equals(dates.date(2011, 1, 9))
def schedule_weekly3():
    "Weekly.next() in middle of interval."
    d1 = dates.date(2011, 1, 3)
    d2 = dates.date(2011, 1, 4)
    return schedule.weekly(('mon', 'sun'), d1).next_step(d2)

@test.equals(dates.date(2011, 1, 9, 12, 10))
def schedule_weekly_next_3():
    "Weekly.next() in middle of interval."
    d1 = dates.date(2011, 1, 3, 12, 10, 00)
    d2 = dates.date(2011, 1, 4, 00, 00, 00)
    return schedule.weekly(('mon', 'sun'), d1).next_step(d2)

@test.equals(dates.date(2011, 1, 7))
def schedule_weeklyl1():
    "Weekly.last() interval rollover."
    d1 = dates.date(2011, 1, 3)
    d2 = dates.date(2011, 1, 8)
    return schedule.weekly(('tue', 'fri'), d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 11))
def schedule_weekly4():
    "Weekly.next() interval rollover."
    d1 = dates.date(2011, 1, 3)
    d2 = dates.date(2011, 1, 8)
    return schedule.weekly(('tue', 'fri'), d1).next_step(d2)

@test.equals(dates.date(2011, 1, 7))
def schedule_weekly5():
    "Weekly.last() rolls back to previous interval."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 12)
    return schedule.weekly(('thu', 'fri'), d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 7, 19, 22))
def schedule_weekly6():
    "Weekly.last() rolls back to previous interval."
    d1 = dates.date(2011, 1, 1, 19, 22)
    d2 = dates.date(2011, 1, 12, 19, 22)
    return schedule.weekly(('thu', 'fri'), d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 13, 19, 22))
def schedule_weekly7():
    "Weekly.next()."
    d1 = dates.date(2011, 1, 1, 19, 22)
    d2 = dates.date(2011, 1, 12, 1, 15)
    return schedule.weekly(('thu', 'fri'), d1).next_step(d2)

@test.equals(dates.date(2011, 1, 21))
def schedule_weekly8():
    "Weekly.next() at the beginning."
    d1 = dates.date(2011, 1, 20) # A Thursday
    return schedule.weekly(('thu', 'fri'), d1).next_step(d1)

@test.equals(dates.datetime(2012, 2, 11, 15, 50, 0))
def schedule_weekly9a():
    "Weekly.last() a moment before a step yields prior step."
    d1 = dates.date(2012, 2, 4, 15, 50, 0)
    d2 = dates.date(2012, 2, 18, 15, 49, 0)
    return schedule.weekly(('sat',), d1).prev_step(d2)

@test.equals(dates.datetime(2012, 2, 11, 15, 50, 0))
def schedule_weekly9b():
    "Weekly.last() exactly on a step yields pervious step."
    d1 = dates.date(2012, 2, 4, 15, 50, 0)
    d2 = dates.date(2012, 2, 18, 15, 50, 0)
    return schedule.weekly(('sat',), d1).prev_step(d2)

@test.equals(dates.datetime(2012, 2, 18, 15, 50, 0))
def schedule_weekly9c():
    "Weekly.last() a moment after a step yields that step."
    d1 = dates.date(2012, 2, 4, 15, 50, 0)
    d2 = dates.date(2012, 2, 18, 15, 51, 0)
    return schedule.weekly(('sat',), d1).prev_step(d2)

@test.equals(dates.datetime(2012, 2, 18, 15, 50, 0))
def schedule_weekly9d():
    "Weekly.last() a moment before a future step yields the prior step."
    d1 = dates.date(2012, 2, 4, 15, 50, 0)
    d2 = dates.date(2012, 2, 25, 15, 49, 0)
    return schedule.weekly(('sat',), d1).prev_step(d2)

@test.true()
def weekly8():
    'Weekly.next_step() was buggy when asking at beginning of its window.'
    now = dates.delta(nHours=1)
    s = schedule.weekly([now.strftime('%a').lower()], now)
    return s.next_step() == now

@test.equals(None)
def schedule_monthly1():
    "Monthly.last() before first recurence is none."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 2)
    return schedule.monthly([5,10,15], d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 5))
def schedule_monthly2():
    "Monthly.last() in middle of schedule."
    lDays = [5, 10, 15]
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 8)
    return schedule.monthly(lDays, d1).prev_step(d2)

@test.equals(dates.date(2011, 5, 15))
def schedule_monthly3():
    "Monthly.last() rolls back to last interval on off months"
    lDays = [5, 10, 15]
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 6, 1)
    return schedule.monthly(lDays, d1, nInterval=2).prev_step(d2)

@test.equals(dates.date(2011, 1, 15))
def schedule_monthly4():
    "Monthly.next() in middle of schedule."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 12)
    return schedule.monthly([5,10,15], d1).next_step(d2)

@test.equals(dates.date(2011, 2, 5))
def schedule_monthly5a():
    "Monthly.next() rolls over to the next interval."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 20)
    return schedule.monthly([5,10,15], d1).next_step(d2)

@test.equals(dates.date(2011, 2, 5, 15, 20))
def schedule_monthly5b():
    "Monthly.next() rolls over to the next interval (minutes honored)."
    d1 = dates.date(2011, 1, 1, 15, 20)
    d2 = dates.date(2011, 1, 15, 15, 21)
    return schedule.monthly([5,10,15], d1).next_step(d2)

@test.equals(dates.date(2012, 3, 1, 20, 57))
def schedule_monthly5c():
    "Monthly.next() rolls over to the next interval when schedule start day after last step this interval."
    d2 = dates.date(2012, 1, 6, 20, 50, 21)
    return schedule.factory(dates.date(2011, 12, 6, 20, 57), None, 'monthly', 3, [1]).next_step(d2)

@test.equals(None)
def schedule_monthly6():
    "Monthly.next() returns none when after end date."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 2, 1)
    d3 = dates.date(2011, 1, 20)
    return schedule.monthly([5,10,15], d1, end = d2).next_step(d3)

@test.equals(dates.date(2011, 1, 15))
def schedule_monthly7():
    "Monthly.next() at the beginning."
    d1 = dates.date(2011, 1, 1)
    return schedule.monthly([1,15], d1).next_step(d1)

@test.equals(None)
def schedule_monthly8():
    "Monthly.last() at the beginning."
    d1 = dates.date(2012, 05, 01, 10, 00)
    d2 = dates.date(2012, 05, 01, 9, 59)
    return schedule.monthly([d1.day], d1).prev_step(d2)

@test.equals(dates.date(2012, 3, 3, 12, 00))
def schedule_monthly9a():
    "Monthly.last() a moment before a step yeilds prior step."
    d1 = dates.date(2012, 3, 3, 12, 00)
    d2 = dates.date(2012, 3, 5, 11, 59)
    return schedule.monthly([3, 5], d1).prev_step(d2)

@test.equals(dates.date(2012, 3, 3, 12, 00))
def schedule_monthly9b():
    "Monthly.last() last a moment after a step yields that step"
    d1 = dates.date(2012, 3, 3, 12, 00)
    d2 = dates.date(2012, 3, 3, 12, 01)
    return schedule.monthly([3, 5], d1).prev_step(d2)

@test.equals(dates.date(2012, 3, 3, 12, 00))
def schedule_monthly9c():
    "Monthly.last() last at the exact time of a step yields previous step"
    d1 = dates.date(2012, 3, 3, 12, 00)
    d2 = dates.date(2012, 3, 5, 12, 00)
    return schedule.monthly([3, 5], d1).prev_step(d2)

@test.equals(None)
def schedule_yearly1():
    "Yearly.last() before start date is none."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 10)
    return schedule.yearly([15,45], d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 15))
def schedule_yearly2():
    "Yearly.last() returns.prev_step 1"
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 16)
    return schedule.yearly([15,45], d1).prev_step(d2)

@test.equals(dates.date(2012, 1, 15))
def schedule_yearly3():
    "Yearly. last() returns prev_step 2."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2012, 1, 16)
    return schedule.yearly([15,45], d1).prev_step(d2)

@test.equals(dates.date(2012, 1, 15))
def schedule_yearly3():
    "Yearly last() returns.prev_step scan 2"
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2012, 1, 16)
    return schedule.yearly([15,45], d1).prev_step(d2)

@test.equals(dates.date(2011, 1, 15))
def schedule_yearly4():
    "Yearly.next() before first recurrence returns first recurrence."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 1, 12)
    return schedule.yearly([15,45], d1).next_step(d2)

@test.equals(dates.date(2011, 2, 14))
def schedule_yearly5():
    "Yearly.last() 3."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 3, 12)
    return schedule.yearly([15,45], d1).prev_step(d2)

@test.equals(dates.date(2012, 1, 15))
def schedule_yearly6():
    "Yearly.next() rolls over to next interval."
    d1 = dates.date(2011, 1, 1)
    d2 = dates.date(2011, 3, 12)
    return schedule.yearly([15,45], d1).next_step(d2)

@test.equals(dates.date(2011, 1, 15))
def schedule_yearly7():
    "Yearly.next() at the beginning."
    d1 = dates.date(2011, 1, 1)
    return schedule.yearly([15,45], d1).next_step(d1)

@test.equals(None)
def schedule_yearly8():
    "Yearly.last() at the beginning"
    d1 = dates.date(2012, 05, 01, 10, 00)
    d2 = dates.date(2012, 05, 01, 9, 59)
    return schedule.yearly([d1.day], d1).prev_step(d2)

@test.equals(dates.date(2012, 3, 3, 12, 00))
def schedule_yearly9a():
    "Yearly.last() a moment before a step yeilds prior step."
    d1 = dates.date(2012, 3, 3, 12, 00)
    d2 = dates.date(2012, 3, 5, 11, 59)
    return schedule.yearly([63, 65], d1).prev_step(d2)

@test.equals(dates.date(2012, 3, 3, 12, 00))
def schedule_yearly9b():
    "Yearly.last() at a moment after step yeilds that step"
    d1 = dates.date(2012, 3, 3, 12, 00) # 63rd day of year
    d2 = dates.date(2012, 3, 3, 12, 01)
    return schedule.yearly([63, 65], d1).prev_step(d2)

@test.equals(dates.date(2012, 3, 3, 12, 00))
def schedule_yearly9c():
    "Yearly.last() last at the exact time of a step yields previous step"
    d1 = dates.date(2012, 3, 3, 12, 00)
    d2 = dates.date(2012, 3, 5, 12, 00)
    return schedule.yearly([63, 65], d1).prev_step(d2)

@test.equals(dates.date(2012, 4, 14, 12, 15))
def schedule_yearly10():
    "Yearly.last() rolls back on off year"
    d1 = dates.date(2012, 1, 5, 12, 15)
    d2 = dates.date(2013, 3, 20)
    # Jan 5, Mar 25, Apr 14 of 2012
    # Jan 5, Mar 26, Apr 16 of 2014
    return schedule.yearly([5,85,105], d1, nInterval=2).prev_step(d2)

@test.equals(dates.date(2014, 3, 26, 12, 15))
def schedule_yearly11():
    "Yearly.next() last step of interval to next interval's first step."
    d1 = dates.date(2012, 1, 5, 12, 15)
    d2 = dates.date(2013, 4, 25, 12, 15)
    # Mar 25, Apr 14 of 2012
    # Mar 26, Apr 15 of 2014
    return schedule.yearly([85,105], d1, nInterval=2).next_step(d2)

@test.equals([dates.date(2012, 1, 4, 12, 00), dates.date(2012, 1, 7, 12, 00), dates.date(2012, 1, 10, 12, 00),
              dates.date(2012, 1, 13, 12, 00), dates.date(2012, 1, 16, 12, 00)])
def schedule_steps1():
    "Can enumerate all the steps of a schedule."
    d1 = dates.date(2012, 1, 4, 12, 00)
    d2 = dates.date(2012, 1, 16, 12, 00)
    sch = schedule.daily(d1, d2, nInterval=3)
    return [ts for ts in sch.steps()]

@test
def schedule_monthly_byweek1():
    "Monthly first Saturday, second Tuesday looking forwards"
    d1 = dates.date(2014, 2, 1)
    s = schedule.monthly([], d1, weeks={1:[5], 2:[1]})
    assert [1,11,] == s.days(d1)
    assert [4,14,] == s.days(dates.date(2014, 1, 1))

@test
def schedule_monthly_byweek2():
    "Monthly fourth Friday looking forwards"
    d1 = dates.date(2014, 2, 1)
    s = schedule.monthly([], d1, weeks={4:[4]})
    assert [28,] == s.days(d1)
    assert [24,] == s.days(dates.date(2014, 1, 1))
    assert [23,] == s.days(dates.date(2015, 1, 1))

@test
def schedule_monthly_byweek3():
    "Monthly last Friday looking forwards"
    d1 = dates.date(2014, 2, 1)
    s = schedule.monthly([], d1, weeks={5:[4]})
    assert [28,] == s.days(d1)
    assert [31,] == s.days(dates.date(2014, 1, 1))
    assert [30,] == s.days(dates.date(2015, 1, 1))

@test
def schedule_monthly_byweek4():
    "Monthly fourth & last can return same day"
    d1 = dates.date(2014, 2, 1)
    s = schedule.monthly([], d1, weeks={4: [0], 5:[0]})
    assert [24,] == s.days(d1)

@test
def factory_validation():
    weeks = {'1': [], '2': [], '3': [], '4': [], '5': []}
    try:
        schedule.factory(dates.now(), None, 'monthly', weeks=weeks)
    except DnaError as e:
        assert e.msgs == [('days', ' : ', 'undefined')]
    try:
        schedule.factory(dates.now(), None, 'monthly', days=[])
    except DnaError as e:
        assert e.msgs == [('days', ' : ', 'undefined')]
    try:
        schedule.factory(dates.now(), None, 'weekly', days=[])
    except DnaError as e:
        assert e.msgs == [('days', ' : ', 'undefined')]

