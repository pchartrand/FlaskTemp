import yaml

from collections import OrderedDict
from .event import Event

class Schedule(object):
    WEEKDAYS = (('MON', 0), ('TUE', 1), ('WED', 2), ('THU', 3), ('FRI', 4), ('SAT', 5), ('SUN', 6))

    def __init__(self):
        self.schedule = OrderedDict()

    def days(self):
        return [d[0] for d in self.WEEKDAYS]

    def week(self):
        return self.days()[0:5]

    def weekend(self):
        return self.days()[5:]

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



    def monday(self):
        return tuple(self.schedule[0].items())

    def tuesday(self):
        return tuple(self.schedule[1].items())

    def wednesday(self):
        return tuple(self.schedule[2].items())

    def thursday(self):
        return tuple(self.schedule[3].items())

    def friday(self):
        return tuple(self.schedule[4].items())

    def saturday(self):
        return tuple(self.schedule[5].items())

    def sunday(self):
        return tuple(self.schedule[6].items())

    def get_temperature_for(self, a_datetime):
        dow = a_datetime.weekday()
        hour = a_datetime.hour
        minute = a_datetime.minute
        yesterday = dow - 1
        if yesterday == -1:
            yesterday = 6
        previous_event = Event(0, 0, self.schedule[yesterday].values()[-1].temperature)
        for event_time in self.schedule[dow]:
            current_event = self.schedule[dow][event_time]
            if current_event.is_before((60*hour + minute), previous_event):
                return previous_event.temperature
            previous_event =  self.schedule[dow][event_time]


def read_schedule(file):
    with open(file,'r') as user_schedule:
        data = yaml.load(user_schedule)

    schedule = Schedule()
    for day, events in data.items():
        for event_data in events:
            event = Event(*[int(e) for e in event_data.split(',')])
            schedule.add_event(day, event)
    return schedule


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


