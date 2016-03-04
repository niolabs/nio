from datetime import timedelta
from time import sleep
from threading import RLock

from nio.util.scheduler.scheduler import Scheduler
from nio.modules.scheduler.job import Job
from nio.util.threading import spawn
from nio.testing.test_case import NIOTestCase


class TestSchedulerCleanUp(NIOTestCase):

    def test_scheduler_cleanup(self):
        """ Asserts that scheduler cleans up its list properly.

        This should occur once a non-repeatable task is executed, and also
        when a repeatable task is cancelled
        """

        scheduler = Scheduler._scheduler_thread._scheduler
        self.assertEqual(len(scheduler._events), 0)
        num_tasks = 2
        for i in range(num_tasks):
            Job(self._callback, timedelta(milliseconds=10), False)
        repeatable_job = Job(self._callback, timedelta(milliseconds=250), True)
        longer_job = Job(self._callback, timedelta(milliseconds=250), False)
        with scheduler._events_lock:
            self.assertEqual(len(scheduler._events), num_tasks + 2)
        self.assertEqual(len(scheduler._queue), num_tasks + 2)
        # sleep enough so that num_tasks are executed
        sleep(0.2)
        with scheduler._events_lock:
            self.assertEqual(len(scheduler._events), 2)
            self.assertIn(longer_job._job, scheduler._events)
            self.assertIn(repeatable_job._job, scheduler._events)
        with scheduler._queue_lock:
            self.assertEqual(len(scheduler._queue), 2)
        # sleep again, now longer_job must be gone
        sleep(0.2)
        with scheduler._events_lock:
            self.assertEqual(len(scheduler._events), 1)
            # and must only remain, the repeatable job
            self.assertIn(repeatable_job._job, scheduler._events)
        with scheduler._queue_lock:
            self.assertEqual(len(scheduler._queue), 1)
        # cancel repeatable job
        repeatable_job.cancel()
        # verify that nothing remains
        with scheduler._events_lock:
            self.assertEqual(len(scheduler._events), 0)
        with scheduler._queue_lock:
            self.assertEqual(len(scheduler._queue), 0)

    def _callback(self):
        pass

    def test_scheduler_cancel_from_callback(self):
        """ Asserts that scheduler accepts callbacks that cancel jobs.  """

        scheduler = Scheduler._scheduler_thread._scheduler

        jobs = []
        num_jobs = 20
        task_duration = num_jobs/100
        jobs_lock = RLock()
        for i in range(num_jobs):
            with jobs_lock:
                jobs.append(Job(self._cancelling_callback,
                                timedelta(seconds=task_duration),
                                True, jobs, jobs_lock))

        # give ample time for jobs to be cancelled
        sleep(num_jobs/10)

        # verify that nothing remains
        with scheduler._events_lock:
            self.assertEqual(len(scheduler._events), 0)
        with scheduler._queue_lock:
            self.assertEqual(len(scheduler._queue), 0)

    def _cancelling_callback(self, jobs, jobs_lock):
        with jobs_lock:
            for job in jobs:
                spawn(job.cancel)
            jobs.clear()
