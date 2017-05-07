from collections import OrderedDict


class StoreCache(object):

    def __init__(self):
        self.cache = OrderedDict()

    def add_to_cache(self, date_value, n, value):
        if not self.cache.get(n):
            self.cache[n] = OrderedDict()
        self.cache[n][date_value] = value

    def get_series(self):
        return self.cache.keys()

    def get_measurements(self, serie):
        serie_as_list = []
        for date_time in self.cache[serie]:
            measurement = dict(
                date=date_time,
                value=self.cache[serie][date_time])
            serie_as_list.append(
                measurement
            )
        return serie_as_list