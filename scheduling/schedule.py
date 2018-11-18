from collections import OrderedDict
from .event import Event

class Schedule(object):
    WEEKDAYS = (('DIM', 0), ('LUN', 1), ('MAR', 2), ('MER', 3), ('JEU', 4), ('VEN', 5), ('SAM', 6))

    def __init__(self):
        self.schedule = OrderedDict()

    def days(self):
        return [d[0] for d in self.WEEKDAYS]

    def week(self):
        return self.days()[1:6]

    def weekend(self):
        return [self.days()[6], self.days()[0]]

    def wd(self, as_code):
        return dict(self.WEEKDAYS)[as_code]

    def weekday(self, as_number):
        for weekday, wd in dict(self.WEEKDAYS).items():
            if wd == as_number:
                return weekday

    def add_event(self, weekday, event):
        assert event.__class__ == Event
        assert weekday in dict(self.WEEKDAYS).keys()
        if self.wd(weekday) not in self.schedule:
            self.schedule[self.wd(weekday)] = OrderedDict()
        time = event.get_time()
        self.schedule[self.wd(weekday)][time] = event

    def print_schedule(self):
        for wd in self.schedule:
            print(self.weekday(wd))
            for event in self.schedule[wd]:
                print(event, self.schedule[wd][event].temperature)

    def sunday(self):
        return tuple(self.schedule[0].items())

    def monday(self):
        return tuple(self.schedule[1].items())

    def tuesday(self):
        return tuple(self.schedule[2].items())

    def wednesday(self):
        return tuple(self.schedule[3].items())

    def thursday(self):
        return tuple(self.schedule[4].items())

    def friday(self):
        return tuple(self.schedule[5].items())

    def saturday(self):
        return tuple(self.schedule[6].items())


def default_schedule():
    night = Event(0, 0, 15)
    wake = Event(6, 0, 18)
    morning = Event(9, 0, 15)
    evening = Event(18, 0, 18)
    late = Event(22, 0, 15)

    a_weekday = (night, wake, morning, evening, late)
    a_week_end_day = (night, Event(9, 30, 19), late)

    schedule = Schedule()

    for weekday in Schedule().week():
        for hour in a_weekday:
            schedule.add_event(weekday, hour)

    for weekend_day in Schedule().weekend():
        for hour in a_week_end_day:
            schedule.add_event(weekend_day, hour)
    return schedule