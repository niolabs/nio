from datetime import timedelta
from threading import RLock

from nio.modules.scheduler.job import Job


class Cache(object):
    """ Utility class to cache and expire items given a certain duration

    There is no distinction as to what kind of items can be cached in a
    given instance, therefore, items of different types can be combined within
    the same cache.
    """

    def __init__(self, duration):
        """ Create a new Cache instance.

        Args:
            duration: default duration in seconds to use for items,
                it can be overriden when adding an item
        """
        self._duration = duration
        self._cache = dict()
        self._cache_lock = RLock()

    def add(self, key, item, duration=None):
        """ Adds an item to the cache

        When an item is added with a positive duration, a job is scheduled
        for its removal at given duration in seconds

        Args:
            key: item key
            item: item value
            duration: if specified item will be kept for this duration in
                seconds, otherwise instance-wide duration is used
        """
        if duration is None:
            # use instance-wide duration when specific duration is not provided
            duration = self._duration

        # is key already in cache
        with self._cache_lock:
            if key in self._cache:
                # cancel job when overriding
                _, job = self._cache.get(key)
                job.cancel()

            if duration > 0:
                # schedule expiration
                job = Job(self._remove_item, timedelta(seconds=duration),
                          False, key)

                # save item in cache
                self._cache[key] = (item, job)

    def get(self, key, default=None):
        """ Gets item from cache

        Args:
            key: item key
            default: value to return when key is not in cache

        Returns:
            item if found, default otherwise
        """
        with self._cache_lock:
            try:
                item, _ = self._cache.get(key)
                return item
            except:
                return default

    def _remove_item(self, key):
        """ Removes item from cache

        This method is triggered when item expires while being called from
        system scheduler.

        Args:
            key: item key
        """
        with self._cache_lock:
            try:
                del self._cache[key]
            except:
                pass
