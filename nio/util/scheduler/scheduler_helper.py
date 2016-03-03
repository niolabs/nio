import heapq
from uuid import uuid4
from datetime import timedelta
from threading import Event, RLock

from nio.util.logging import get_nio_logger
from nio.util.threading import spawn
from time import time, sleep
from collections import namedtuple

QueueEvent = namedtuple('Event', 'time, id, target, frequency, args, kwargs')


class SchedulerHelper(object):

    def __init__(self, resolution, min_delta):
        """ Initializes scheduler.

        Args:
            resolution: Specifies the scheduler resolution, this value
                is used during sleeping operations when it is determined
                a wait is needed before determining the next event to be
                executed
            min_delta: minimum value to consider when scheduling a task
        """
        super().__init__()

        self._resolution = resolution
        self._min_delta = min_delta

        self.logger = get_nio_logger("Custom Scheduler")
        self._queue = []
        self._queue_lock = RLock()
        self._stop_event = Event()
        self._events = dict()
        self._events_lock = RLock()

    def start(self):
        """ Starts scheduler.

        """

        while not self._stop_event.is_set():

            try:
                event = None
                with self._queue_lock:
                    queue_length = len(self._queue)
                    self.logger.debug('Queue contains: {0} tasks'.
                                      format(queue_length))

                    if queue_length:
                        # have access to first in time to execute event
                        event = heapq.heappop(self._queue)

                if not event:
                    sleep(self._resolution)
                    continue

                # if there are events, check their time to see if
                # it is up for firing it.
                event_time, event_id, target, frequency, args, kwargs = event
                now = time()
                # find out if need to sleep or execute event
                if now < event_time:
                    self.logger.debug(
                        'Current task time has not been reached, {0} remains'.
                        format(event_time - now))

                    with self._queue_lock:
                        # push it back when event is not ready
                        heapq.heappush(self._queue, event)
                    # do not allow big sleeps, have some control over it
                    # in case scheduler is stopped
                    delay = min(event_time - now, self._resolution)
                    sleep(delay)
                else:
                    # time is up, execute
                    try:
                        self.logger.debug("Executing: {0}".format(target))
                        # launch target task from a different thread thus
                        # making scheduler independent from task duration
                        spawn(target, *args, **kwargs)
                    except Exception:
                        self.logger.exception('Calling: {0}'.format(target))

                    with self._events_lock:
                        # before processing any further, make sure event has
                        # not been cancelled
                        if event_id in self._events:
                            # is it repeatable?
                            if frequency:
                                # reschedule it back, adding frequency to
                                # event time
                                event = QueueEvent(event_time + frequency,
                                                   event_id,
                                                   target,
                                                   frequency,
                                                   args, kwargs)
                                # housekeeping new event in
                                with self._queue_lock:
                                    heapq.heappush(self._queue, event)
                                self._events[event_id] = event
                            else:
                                # remove event when not repeatable
                                self._events.pop(event_id)
                        else:
                            self.logger.debug("Event: {0} was cancelled".
                                              format(event_id))

            except Exception:
                # log any exception in this big try/except
                # and do not leave loop
                self.logger.exception('Exception caught')

    def stop(self):
        """ Stops scheduler.

        """
        self._stop_event.set()

    def add(self, target, delta, repeatable, *args, **kwargs):
        """ Adds an event to the scheduler.

        Args:
            target (callable): The task to be scheduled.
            delta (timedelta): The scheduling delta. The scheduler will
                wait for this delta before running 'target' for the first
                time.
            repeatable (bool): When False, 'target' is run only once.
                Otherwise, it is run repeatedly at an delta defined by
                'delta'.
            args: Positional arguments to be passed to 'target'.
            kwargs: Keyword arguments to be passed to 'target'.

        Returns:
            Event Identifier, which can be used for cancellation

        """
        if not isinstance(delta, timedelta):
            raise AttributeError('delta must be of type: timedelta')

        delta = delta.total_seconds()
        if repeatable:
            # make sure delta is not smaller than minimum
            if delta < self._min_delta:
                delta = self._min_delta
            frequency = delta
        else:
            # when non repeatable, allow delta to be as small as user wishes
            # it to be
            frequency = 0

        event_id = uuid4().hex
        event = QueueEvent(time() + delta, event_id, target, frequency,
                           args, kwargs)

        # add to queue
        with self._queue_lock:
            heapq.heappush(self._queue, event)

        # add to events
        with self._events_lock:
            self._events[event_id] = event

        return event_id

    def cancel(self, event_id):
        """ Cancels an event scheduled for execution.

        Args:
            event_id: Event Id obtained from an "add" call

        Returns:
            True: If event was previously scheduled
            False: otherwise

        """
        # remove it from events dictionary
        event = None
        with self._events_lock:
            if event_id in self._events:
                event = self._events.pop(event_id)
        if event:
            try:
                with self._queue_lock:
                    self._queue.remove(event)
                    heapq.heapify(self._queue)
                self.logger.debug('Success cancelling event')
                return True
            except Exception:
                self.logger.debug('Failure to remove event {0} from queue'
                                  ' while cancelling a job'.format(event))
        return False
