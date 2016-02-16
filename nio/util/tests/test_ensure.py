from nio.util.ensure_types import ensure_is, ensure_list
from nio.util.support.test_case import NIOTestCase


class TestEnsure(NIOTestCase):

    def test_ensure_list(self):
        some_string = 'astring'

        lst = ensure_list([some_string])
        self.assertEqual(lst, [some_string])

        lst = ensure_list(some_string)
        self.assertTrue(isinstance(lst, list))
        self.assertEqual(lst, [some_string])

        with self.assertRaises(TypeError):
            ensure_list(some_string, TypeError)

        lst = ensure_list([some_string], TypeError)
        self.assertEqual(lst, [some_string])

    def test_ensure_is(self):
        some_string = 'astring'

        lst1 = ensure_is((some_string, ), [list, tuple], lambda x: [x])
        lst2 = ensure_is([some_string], [list, tuple], lambda x: [x])
        self.assertEqual(lst1, (some_string, ))
        self.assertEqual(lst2, [some_string])

        dct = ensure_is(some_string, [list, tuple], lambda x: {'key': x})
        self.assertTrue(isinstance(dct, dict))
        self.assertDictEqual(dct, {'key': some_string})

        with self.assertRaises(TypeError):
            ensure_is(some_string, [list, tuple], TypeError)

        lst = ensure_is({'key': some_string}, [list, tuple, dict], TypeError)
        self.assertDictEqual(lst, {'key': some_string})
