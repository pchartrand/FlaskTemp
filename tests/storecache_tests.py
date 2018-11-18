from unittest import TestCase
from storecache import StoreCache

class StoreCacheTests(TestCase):
    def test_can_store_to_cache_given_a_serie_key(self):
        cache = StoreCache()
        serie_key = 0

        cache.add_to_cache(serie_key, '2016-04-01 12:45:51', 1.0)

        self.assertEqual(1, len(cache.get_series()))

    def test_series_names_are_arbitrary_and_are_preserved(self):
        cache = StoreCache()

        cache.add_to_cache(0, '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache('my_serie', '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache('my_serie', '2016-04-01 12:45:52', 1.1)

        series = cache.get_series()
        self.assertEqual(0, series[0])
        self.assertEqual('my_serie', series[1])
        self.assertEqual(1, cache.measurements_count(0))
        self.assertEqual(1, cache.measurements_count())
        self.assertEqual(2, cache.measurements_count('my_serie'))
        self.assertEqual('2016-04-01 12:45:51', cache.oldest(0))

    def test_can_recover_series_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache(0, '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache(0, '2016-04-01 12:45:52', 1.1)
        cache.add_to_cache(0, '2016-04-01 12:45:53', 1.1)
        cache.add_to_cache(1, '2016-04-01 12:45:54', 1.1)
        cache.add_to_cache(1, '2016-04-01 12:45:55', 1.1)
        cache.add_to_cache(2, '2016-04-01 12:45:56', 1.1)

        series = cache.get_series()

        self.assertEqual(3, len(series))
        self.assertEqual(3, cache.measurements_count(0))
        self.assertEqual(2, cache.measurements_count(1))
        self.assertEqual(1, cache.measurements_count(2))
        self.assertEqual('2016-04-01 12:45:51', cache.oldest(0))
        self.assertEqual('2016-04-01 12:45:54', cache.oldest(1))
        self.assertEqual('2016-04-01 12:45:56', cache.oldest(2))


    def test_series_are_stored_sequentially(self):
        cache = StoreCache()
        cache.add_to_cache(3, '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache(1, '2016-04-01 12:45:52', 1.1)

        series = cache.get_series()

        self.assertEqual(3, series[0])
        self.assertEqual(1, series[1])


    def test_can_recover_various_series_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache(1, '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache(3, '2016-04-01 12:45:52', 1.0)
        cache.add_to_cache(3, '2016-04-01 12:45:53', 1.1)
        cache.add_to_cache(3, '2016-04-01 12:45:54', 1.2)

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
        cache.add_to_cache(3, '2016-04-01 12:45:53', 1.2)
        cache.add_to_cache(3, '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache(3, '2016-04-01 12:45:52', 1.1)

        serie = cache.get_measurements(3)

        self.assertEqual(3, len(serie))
        self.assertEqual(1.2, serie[0]['value'])
        self.assertEqual(1.0, serie[1]['value'])
        self.assertEqual(1.1, serie[2]['value'])

    def test_key_for_serie_is_datetime_string(self):
        cache = StoreCache()
        cache.add_to_cache(3, '2016-04-01 12:45:51', 1.0)
        cache.add_to_cache(3, '2016-04-01 12:45:51', 1.1)
        cache.add_to_cache(3, '2016-04-01 12:45:51', 1.2)

        serie = cache.get_measurements(3)

        self.assertEqual(1, len(serie))
        self.assertEqual(1.2, serie[0]['value'])

    def test_can_remove_old_data_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache(1, '2016-04-01 12:45:52', 1.0)
        cache.add_to_cache(1, '2016-04-01 12:45:53', 1.1)
        cache.add_to_cache(1, '2016-04-01 12:45:54', 1.2)
        cache.add_to_cache(1, '2016-04-01 12:45:55', 1.3)

        cache.delete_older_than(1, '2016-04-01 12:45:54')
        serie = cache.get_measurements(1)
        self.assertEqual(2, len(serie))


    def test_can_remove_old_data_from_cache_even_when_no_seconds_are_kept(self):
        cache = StoreCache()
        cache.add_to_cache(1, '2016-04-01 12:45', 1.0)
        cache.add_to_cache(1, '2016-04-01 12:46', 1.1)
        cache.add_to_cache(1, '2016-04-01 12:47', 1.2)
        cache.add_to_cache(1, '2016-04-01 12:48', 1.3)

        cache.delete_older_than(1, '2016-04-01 12:45:54')
        serie = cache.get_measurements(1)
        self.assertEqual(3, len(serie))

    def test_cat_retrieve_closest_previous_item_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache(1, '2016-04-01 12:45', 1.0)
        cache.add_to_cache(1, '2016-04-01 12:50', 1.1)
        cache.add_to_cache(1, '2016-04-01 12:55', 1.2)
        cache.add_to_cache(1, '2016-04-01 12:60', 1.3)

        date_time, value = cache.return_closest_previous_value(1, '2016-04-01 12:52')

        self.assertEqual(1.1, value)
        self.assertEqual('2016-04-01 12:50', date_time)

    def test_cat_retrieve_closest_following_item_from_cache(self):
        cache = StoreCache()
        cache.add_to_cache(1, '2016-04-01 12:45', 1.0)
        cache.add_to_cache(1, '2016-04-01 12:50', 1.1)
        cache.add_to_cache(1, '2016-04-01 12:55', 1.2)
        cache.add_to_cache(1, '2016-04-01 12:60', 1.3)

        date_time, value = cache.return_closest_following_value(1, '2016-04-01 12:52')

        self.assertEqual(1.2, value)
        self.assertEqual('2016-04-01 12:55', date_time)
