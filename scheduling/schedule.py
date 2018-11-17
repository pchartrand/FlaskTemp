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

