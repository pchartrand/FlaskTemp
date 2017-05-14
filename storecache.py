from collections import OrderedDict


class StoreCache(object):

    def __init__(self):
        self._cache = OrderedDict()

    def add_to_cache(self, serie, date_value, value):
        if not self._cache.get(serie):
            self._cache[serie] = OrderedDict()
        self._cache[serie][date_value] = value

    def get_series(self):
        return self._cache.keys()

    def get_measurements(self, serie):
        serie_as_list = []
        for date_time in self._cache[serie]:
            measurement = dict(
                date=date_time,
                value=self._cache[serie][date_time]
            )
            serie_as_list.append(
                measurement
            )
        return serie_as_list

    def delete_older_than(self, serie, date_value):
        for date_time in self._cache[serie]:
            if (date_time < date_value):
                del self._cache[serie][date_time]


    def delete_everything_older_than(self, date_value):
        for serie in self.get_series():
            self.delete_older_than(serie, date_value)