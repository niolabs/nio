import copy
import datetime
from nio.common.signal.base import Signal
from nio.util.support.test_case import NIOTestCase


class TestSignal(NIOTestCase):

    def setUp(self):
        super().setUp()
        self.attrs = {
            'foo': 'bar',
            'num': 3,
            'dt': datetime.date(2010, 3, 14)
        }

    def test_from_dict(self):
        sig = Signal()
        self.assertFalse(hasattr(sig, 'foo'))
        sig.from_dict(self.attrs)
        self.assertTrue(hasattr(sig, 'foo'))
        self.assertEqual(sig.foo, 'bar')

    def test_construct(self):
        sig = Signal(self.attrs)
        self.assertTrue(hasattr(sig, 'foo'))
        self.assertEqual(sig.foo, 'bar')

    def test_signal_str(self):
        """ Assert that str-ing a signal calls to_dict on it"""
        sig = Signal(self.attrs)
        sig_str = str(sig)
        # Can only compare lengths since str changes the order some time
        self.assertEqual(len(sig_str), len(str(self.attrs)))

    def test_no_hidden(self):
        sig = Signal({
            'not_hidden': 'yes',
            '_hidden': 'no'
        })
        self.assertIn('not_hidden', sig.to_dict())
        self.assertNotIn('_hidden', sig.to_dict())

    def test_to_dict_with_type(self):
        sig = Signal(self.attrs)
        signal_dict = sig.to_dict(True)
        self.assertIn('_type', signal_dict)
        self.assertIn('foo', signal_dict)

    def test_to_dict_keeps_types(self):
        sig = Signal(self.attrs)
        signal_dict = sig.to_dict()
        self.assertEqual(signal_dict['num'], 3)
        self.assertEqual(signal_dict['dt'], datetime.date(2010, 3, 14))

    def test_to_dict_with_errors(self):
        sig = Signal(
            {'': 'empty string',
             None: 'none key',
             False: 'false key',
             "allowed": "allowed_value",
             1: "one"})
        self.assertFalse(hasattr(sig, ""))
        self.assertFalse(hasattr(sig, "None"))
        self.assertFalse(hasattr(sig, "False"))
        self.assertTrue(hasattr(sig, "allowed"))
        self.assertFalse(hasattr(sig, "1"))

    def test_to_dict_with_hidden(self):
        attributes = copy.deepcopy(self.attrs)
        attributes["_hidden1"] = "hidden1"
        attributes["_hidden2"] = "hidden2"
        sig = Signal(attributes)
        signal_dict = sig.to_dict(hidden=True)
        for key, value in self.attrs.items():
            self.assertEqual(signal_dict[key], value)
        self.assertEqual(signal_dict['_hidden1'], attributes["_hidden1"])
        self.assertEqual(signal_dict['_hidden2'], attributes["_hidden2"])

        # use default
        signal_dict = sig.to_dict()
        for key, value in self.attrs.items():
            self.assertEqual(signal_dict[key], value)
        self.assertNotIn('_hidden1', signal_dict)
        self.assertNotIn('_hidden2', signal_dict)
