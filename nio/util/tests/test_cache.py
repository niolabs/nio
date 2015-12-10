from time import sleep

from nio.util.threading import spawn
from nio.util.cache import Cache
from nio.util.support.test_case import NIOTestCase


class TestCache(NIOTestCase):

    def test_add(self):
        """ Adding an item that overrides duration
        """
        cache = Cache(0.5)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        cache.add(key, item, duration=0.1)
        self.assertEqual(cache.get(key), item)
        sleep(0.15)
        self.assertIsNone(cache.get(key))

    def test_duration_not_specified(self):
        """ Adding an item that does not specifies duration
        """

        cache = Cache(0.1)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        cache.add(key, item)
        self.assertEqual(cache.get(key), item)
        sleep(0.15)
        self.assertIsNone(cache.get(key))

    def test_no_duration(self):
        """ Verifies that when duration is 0 nothing gets added
        """

        cache = Cache(0)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        cache.add(key, item)
        self.assertIsNone(cache.get(key))

    def test_item_with_zero_duration(self):
        """ Verifies that when the item is added with 0 duration
        nothing is added (default duration does not apply)
        """

        cache = Cache(2)

        key = 1
        item = "1"
        self.assertIsNone(cache.get(key))
        cache.add(key, item, 0)
        self.assertIsNone(cache.get(key))

    def test_default_when_item_is_missing(self):
        """ Verifies that when the item does not exists and a default
        return is specified, such default is retrieved
        """

        cache = Cache(2)
        self.assertEqual(cache.get("not existant", "default to be retrieved"),
                         "default to be retrieved")

    def test_multithreading(self):
        """ Verifies that adding from multiple threads keeps results as expected
        """
        num_threads = 20
        cache = Cache(0.2)
        for i in range(num_threads):
            spawn(cache.add, "key{0}".format(i), i)
        sleep(0.1)
        # assert all items are in cache, and with the right values
        self.assertEqual(len(cache._cache), num_threads)
        for i in range(num_threads):
            self.assertEqual(cache.get("key{0}".format(i)), i)
        # allow items to expire
        sleep(0.15)
        # assert all items expired
        self.assertEqual(len(cache._cache), 0)

    def test_adding_same_key(self):
        """ Make sure item for a given key can be overriden before it expires
        and that it is correctly retrieved
        """

        cache = Cache(0.4)

        key = 1
        item = "1"
        cache.add(key, item)
        self.assertEqual(cache.get(key), item)
        sleep(0.3)
        item = "2"
        cache.add(key, item)
        sleep(0.3)
        self.assertEqual(cache.get(key), item)
