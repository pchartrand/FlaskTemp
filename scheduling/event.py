class Event(object):
    def __init__(self, hour, minute, temperature):
        assert 0 <= hour < 24
        assert 0 <= minute < 60
        assert 5 <= temperature < 26
        self.hour = hour
        self.minute = minute
        self.temperature = temperature

    def get_time(self):
        return "%02d:%02d" % (self.hour, self.minute)