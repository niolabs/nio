from nio.util.support.test_case import NIOTestCase
from nio.modules.persistence import Persistence


class TestPersistence(NIOTestCase):

    def get_test_modules(self):
        return super().get_test_modules() | {'persistence'}

    def test_default_persist(self):
        """ Make sure we can still retrieve values after they are stored """

        persist = Persistence('Default Persistence')
        persist.store('test_key', 'test_val')

        # Make sure we get the saved value
        self.assertEqual(
            persist.load('test_key', 'not found'),
            'test_val')

        # Make sure we get a default value if one hasn't been saved
        self.assertEqual(
            persist.load('not_a_key', 'default_val'),
            'default_val')

        # Make sure has key works properly too
        self.assertTrue(persist.has_key('test_key'))  # nopep8
        self.assertFalse(persist.has_key('not_a_key'))  # nopep8

        # Make sure saving has no effect on our loaded values
        persist.save()
        self.assertEqual(
            persist.load('test_key', 'not found'),
            'test_val')
        self.assertEqual(
            persist.load('not_a_key', 'default_val'),
            'default_val')

        # Make sure we can clear values and that they go away
        persist.clear('test_key')
        self.assertEqual(
            persist.load('test_key', 'not found'),
            'not found')
        self.assertEqual(
            persist.load('not_a_key', 'default_val'),
            'default_val')
        self.assertFalse(persist.has_key('test_key'))  # nopep8
        self.assertFalse(persist.has_key('not_a_key'))  # nopep8
