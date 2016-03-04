from enum import Enum
from unittest.mock import Mock

from nio.util.flags_enum import FlagsEnum, InvalidFlag
from nio.testing.test_case import NIOTestCase


class Status(Enum):
    created = 1
    stopped = 2
    started = 3
    stopping = 4
    deliver_signal_error = 5


class OtherStatus(Enum):
    created = 1
    two = 2


class TestFlagsEnum(NIOTestCase):

    def test_add_remove(self):
        # assert that initialization, add, remove, and is_set
        # work as expected

        status = FlagsEnum(Status)
        self.assertFalse(status.is_set(Status.created))
        self.assertFalse(status.is_set(Status.stopped))
        self.assertFalse(status.is_set(Status.started))
        self.assertFalse(status.is_set(Status.stopping))
        self.assertFalse(status.is_set(Status.deliver_signal_error))

        status.add(Status.deliver_signal_error)
        self.assertFalse(status.is_set(Status.created))
        self.assertFalse(status.is_set(Status.stopped))
        self.assertFalse(status.is_set(Status.started))
        self.assertFalse(status.is_set(Status.stopping))
        self.assertTrue(status.is_set(Status.deliver_signal_error))

        status.add(Status.started)
        self.assertFalse(status.is_set(Status.created))
        self.assertFalse(status.is_set(Status.stopped))
        self.assertTrue(status.is_set(Status.started))
        self.assertFalse(status.is_set(Status.stopping))
        self.assertTrue(status.is_set(Status.deliver_signal_error))

        status.remove(Status.deliver_signal_error)
        self.assertFalse(status.is_set(Status.created))
        self.assertFalse(status.is_set(Status.stopped))
        self.assertTrue(status.is_set(Status.started))
        self.assertFalse(status.is_set(Status.stopping))
        self.assertFalse(status.is_set(Status.deliver_signal_error))

    def test_default_flag(self):
        # assert that it can be initialized with a flag

        status = FlagsEnum(Status, Status.created)
        self.assertTrue(status.is_set(Status.created))
        self.assertFalse(status.is_set(Status.stopped))
        self.assertFalse(status.is_set(Status.started))
        self.assertFalse(status.is_set(Status.stopping))
        self.assertFalse(status.is_set(Status.deliver_signal_error))

    def test_callback(self):
        # assert that it can be initialized with a flag
        self._callback_called = False
        status = FlagsEnum(Status,
                           status_change_callback=self._status_change_callback)

        self.assertFalse(self._callback_called)

        self.assertFalse(status.is_set(Status.created))
        self.assertFalse(status.is_set(Status.stopped))
        self.assertFalse(status.is_set(Status.started))
        self.assertFalse(status.is_set(Status.stopping))
        self.assertFalse(status.is_set(Status.deliver_signal_error))

        status.set(Status.created)
        self.assertTrue(self._callback_called)
        self._callback_called = False
        # assert that there was no change in status since no callback
        # was fired
        status.set(Status.created)
        self.assertFalse(self._callback_called)
        status.set(Status.stopping)
        self.assertTrue(self._callback_called)
        self._callback_called = False
        self.assertFalse(status.is_set(Status.created))
        self.assertTrue(status.is_set(Status.stopping))

        status.add(Status.stopping)
        self.assertFalse(self._callback_called)

        status.remove(Status.created)
        self.assertFalse(self._callback_called)

        status.set(Status.stopping)
        self.assertFalse(self._callback_called)

        status.remove(Status.stopping)
        self.assertTrue(self._callback_called)

    def _status_change_callback(self, old_status, new_status):
        self._callback_called = True
        self.assertNotEqual(old_status, new_status)

    def test_bad_params(self):
        # assert that it fails when passing something other than a Status enum

        status = FlagsEnum(Status)
        with self.assertRaises(InvalidFlag):
            status.add(OtherStatus.created)

        with self.assertRaises(InvalidFlag):
            status.add(4)

    def test_equals_flag(self):
        status = FlagsEnum(Status)

        status.set(Status.created)
        self.assertTrue(status == Status.created)
        self.assertEqual(status, Status.created)

        status.set(Status.started)
        self.assertFalse(status == Status.created)
        self.assertNotEqual(status, Status.created)
        self.assertTrue(status == Status.started)
        self.assertEqual(status, Status.started)

        status.add(Status.created)
        self.assertFalse(status == Status.created)
        self.assertNotEqual(status, Status.created)
        self.assertFalse(status == Status.started)
        self.assertNotEqual(status, Status.started)

        status.remove(Status.created)
        self.assertFalse(status == Status.created)
        self.assertNotEqual(status, Status.created)
        self.assertTrue(status == Status.started)
        self.assertEqual(status, Status.started)

    def test_equals_instance(self):
        status1 = FlagsEnum(Status)
        status2 = FlagsEnum(Status)

        status1.set(Status.created)
        self.assertNotEqual(status1, status2)

        status2.set(Status.started)
        self.assertNotEqual(status1, status2)

        status2.remove(Status.started)
        self.assertNotEqual(status1, status2)

        status2.set(Status.created)
        self.assertEqual(status1, status2)

        status1.remove(Status.created)
        self.assertNotEqual(status1, status2)

    def test_cloning(self):
        status = FlagsEnum(Status)
        status.add(Status.created)
        status.add(Status.stopping)
        import copy

        cloned_status = copy.deepcopy(status)
        self.assertTrue(cloned_status.is_set(Status.created))
        self.assertTrue(cloned_status.is_set(Status.stopping))
        self.assertFalse(cloned_status.is_set(Status.started))
        self.assertFalse(cloned_status.is_set(Status.stopped))
        self.assertFalse(cloned_status.is_set(Status.deliver_signal_error))

        # verify that it is ok to clone an already cloned instance.
        cloned_twice_status = copy.deepcopy(cloned_status)
        self.assertTrue(cloned_twice_status.is_set(Status.created))
        self.assertTrue(cloned_twice_status.is_set(Status.stopping))
        self.assertFalse(cloned_twice_status.is_set(Status.started))
        self.assertFalse(cloned_twice_status.is_set(Status.stopped))
        self.assertFalse(
            cloned_twice_status.is_set(Status.deliver_signal_error))

    def test_flags_assignment(self):
        # assert that when flags are assigned, change callback is triggered
        # as expected
        status = FlagsEnum(Status,
                           status_change_callback=Mock())

        self.assertEqual(status._status_change_callback.call_count, 0)
        status_to_assign = FlagsEnum(Status,
                                     status_change_callback=Mock())
        status_to_assign.add(Status.created)
        status.flags = status_to_assign.flags
        self.assertEqual(status._status_change_callback.call_count, 1)

        # removing created, adding started
        status_to_assign.remove(Status.created)
        status_to_assign.add(Status.started)
        status.flags = status_to_assign.flags
        self.assertEqual(status._status_change_callback.call_count, 2)

        # no change
        status.flags = status_to_assign.flags
        self.assertEqual(status._status_change_callback.call_count, 2)

        # removing started
        status_to_assign.remove(Status.started)
        status.flags = status_to_assign.flags
        self.assertEqual(status._status_change_callback.call_count, 3)
