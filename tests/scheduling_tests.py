from unittest import TestCase
from scheduling.schedule import Schedule, Event


class EventTests(TestCase):
    def test_can_create_an_event(self):
        event = Event(8, 30, 17)
        assert event.temperature == 17
        assert event.minute == 30
        assert event.hour == 8
        assert event.get_time() == '08:30'

    def test_event_hour_is_valid(self):
        try:
            Event(25, 30, 17)
            raise Exception("should have raised an assertion error")
        except AssertionError:
            pass

    def test_event_minute_is_valid(self):
        try:
            Event(5, 60, 17)
            raise Exception("should have raised an assertion error")
        except AssertionError:
            pass

    def test_event_temperature_is_not_to_high(self):
        try:
            Event(5, 30, 26)
            raise Exception("should have raised an assertion error")
        except AssertionError:
            pass

    def test_event_temperature_is_not_too_low(self):
        try:
            Event(5, 30, 4)
            raise Exception("should have raised an assertion error")
        except AssertionError:
            pass

    def test_can_get_an_ordered_list_of_days(self):
        schedule = Schedule()
        days = schedule.days()
        for wd in ('DIM', 'LUN', 'MAR', 'MER', 'JEU', 'VEN', 'SAM'):
            w = days.pop(0)
            self.assertEqual(wd, w, "expected {} got {}".format(wd, w))


class ScheduleTests(TestCase):
    def test_can_get_an_ordered_list_of_week_days(self):
        schedule = Schedule()
        days = schedule.week()
        for wd in ('LUN', 'MAR', 'MER', 'JEU', 'VEN'):
            w = days.pop(0)
            self.assertEqual(wd, w, "expected {} got {}".format(wd, w))

    def test_can_get_an_ordered_list_of_weekend_days(self):
        schedule = Schedule()
        days = schedule.weekend()
        for wd in ('SAM','DIM'):
            w = days.pop(0)
            self.assertEqual(wd, w, "expected {} got {}".format(wd, w))

    def test_can_create_a_schedule(self):

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

        assert len(schedule.schedule) == 7  # days in the week
        assert len(schedule.schedule[2]) == 5  # events in a weekday
        self.assertEqual(
            3,  # events in a weekend day
            len(schedule.schedule[6]),
            'expected {} got {}'.format(3,len(schedule.schedule[6]))
        )

        assert schedule.schedule[2]['06:00'] == wake
        assert schedule.schedule[3]['09:00'] == morning
        assert schedule.schedule[4]['18:00'] == evening

        assert schedule.schedule[schedule.wd('DIM')]['09:30'].temperature == 19
        schedule.print_schedule()