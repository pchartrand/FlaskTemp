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

    def measurements_count(self, serie=None):
        if len(self._cache) > 0:
            if serie is None:
                serie = self._cache.keys()[0]
            return len(self._cache[serie])
        return 0

    def oldest(self, serie):
        return self._cache[serie].keys()[0]

    def delete_older_than(self, serie, date_value):
        for date_time in self._cache[serie]:
            if (date_time < date_value):
                del self._cache[serie][date_time]


    def return_closest_following_value(self, serie, date_value):
        for date_time in self._cache[serie]:
            if (date_time > date_value):
                return date_time, self._cache[serie][date_time]


    def return_closest_previous_value(self, serie, date_value):
        previous_value = None
        previous_date_time = None
        for date_time in self._cache[serie]:
            if (date_time > date_value):
                return previous_date_time, previous_value
            else:
                previous_date_time = date_time
                previous_value = self._cache[serie][date_time]


    def delete_everything_older_than(self, date_value):
        for serie in self.get_series():
            self.delete_older_than(serie, date_value)