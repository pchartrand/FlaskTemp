from unittest import TestCase
from storecache import StoreCache

class StoreCacheTests(TestCase):
    def test_can_store_to_cache(self):
        cache = StoreCache()

        self.assertEqual(0, len(cache.cache))

        cache.add_to_cache('2016-04-01 12:45:51', 0, 1.0)

        self.assertEqual(1, len(cache.cache))

    def test_can_recover_series_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache('2016-04-01 12:45:51', 0, 1.0)
        cache.add_to_cache('2016-04-01 12:45:52', 0, 1.1)
        cache.add_to_cache('2016-04-01 12:45:53', 0, 1.1)
        cache.add_to_cache('2016-04-01 12:45:54', 1, 1.1)
        cache.add_to_cache('2016-04-01 12:45:55', 1, 1.1)
        cache.add_to_cache('2016-04-01 12:45:56', 2, 1.1)

        series = cache.get_series()

        self.assertEqual(3, len(series))

    def test_series_are_stored_sequentially(self):
        cache = StoreCache()
        cache.add_to_cache('2016-04-01 12:45:51', 3, 1.0)
        cache.add_to_cache('2016-04-01 12:45:52', 1, 1.1)

        series = cache.get_series()

        self.assertEqual(3, series[0])
        self.assertEqual(1, series[1])


    def test_can_recover_various_series_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache('2016-04-01 12:45:51', 1, 1.0)
        cache.add_to_cache('2016-04-01 12:45:52', 3, 1.0)
        cache.add_to_cache('2016-04-01 12:45:53', 3, 1.1)
        cache.add_to_cache('2016-04-01 12:45:54', 3, 1.2)

        serie1 = cache.get_measurements(1)
        serie2 = cache.get_measurements(3)

        self.assertEqual(1, len(serie1))
        self.assertEqual(1.0, serie1[0]['value'])

        self.assertEqual(3, len(serie2))
        self.assertEqual(1.0, serie2[0]['value'])
        self.assertEqual(1.1, serie2[1]['value'])
        self.assertEqual(1.2, serie2[2]['value'])

    def test_values_are_stored_sequentially_in_serie(self):
        cache = StoreCache()
        cache.add_to_cache('2016-04-01 12:45:53', 3, 1.2)
        cache.add_to_cache('2016-04-01 12:45:51', 3, 1.0)
        cache.add_to_cache('2016-04-01 12:45:52', 3, 1.1)

        serie = cache.get_measurements(3)

        self.assertEqual(3, len(serie))
        self.assertEqual(1.2, serie[0]['value'])
        self.assertEqual(1.0, serie[1]['value'])
        self.assertEqual(1.1, serie[2]['value'])

    def test_key_for_serie_is_datetime_string(self):
        cache = StoreCache()
        cache.add_to_cache('2016-04-01 12:45:51', 3, 1.0)
        cache.add_to_cache('2016-04-01 12:45:51', 3, 1.1)
        cache.add_to_cache('2016-04-01 12:45:51', 3, 1.2)

        serie = cache.get_measurements(3)

        self.assertEqual(1, len(serie))
        self.assertEqual(1.2, serie[0]['value'])