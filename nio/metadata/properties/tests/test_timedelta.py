from datetime import timedelta
from nio.util.support.test_case import NIOTestCase
from nio.metadata.properties.holder import PropertyHolder
from nio.metadata.properties.timedelta import TimeDeltaProperty


class SampleClass(PropertyHolder):
    timedelta_property = TimeDeltaProperty()
    timedelta_default = TimeDeltaProperty(default={"seconds": 90})


class TestTimeDeltaProp(NIOTestCase):
    def test_initialization(self):
        instance = SampleClass()

        self.assertIsNotNone(instance.timedelta_property)

    def test_default_value(self):
        class DefaultSampleClass(PropertyHolder):
            timedelta_dict_property = TimeDeltaProperty(
                default={"weeks": 1})
            timedelta_td_property = TimeDeltaProperty(
                default=timedelta(weeks=1))

        inst = DefaultSampleClass()
        self.assertNotEqual(inst.timedelta_dict_property(), timedelta(days=6))
        self.assertEqual(inst.timedelta_dict_property(), timedelta(days=7))
        self.assertNotEqual(inst.timedelta_dict_property(), timedelta(days=8))

        self.assertNotEqual(inst.timedelta_td_property(), timedelta(days=6))
        self.assertEqual(inst.timedelta_td_property(), timedelta(days=7))
        self.assertNotEqual(inst.timedelta_td_property(), timedelta(days=8))

    def test_accept_values(self):
        instance = SampleClass()

        instance.timedelta_property = timedelta(seconds=3)
        self.assertEqual(instance.timedelta_property().total_seconds(), 3)

        self.assertEqual(instance.timedelta_property(), timedelta(seconds=3))

    def test_serialize_deserialize_matching(self):
        instance1 = SampleClass()
        instance1.timedelta_property = timedelta(days=1,
                                                 seconds=1,
                                                 microseconds=1,
                                                 milliseconds=1,
                                                 minutes=1,
                                                 hours=1,
                                                 weeks=1)
        instance1_serialized = instance1.to_dict()

        # set up instance 2 from instance1 serialization
        instance2 = SampleClass()
        instance2.from_dict(instance1_serialized)
        instance2_serialized = instance2.to_dict()

        self.assertEqual(instance1_serialized, instance2_serialized)
        self.assertEqual(instance1.timedelta_property(),
                         instance2.timedelta_property())

    def test_json_serializable(self):
        instance1 = SampleClass()
        instance1.timedelta_property = timedelta(days=1,
                                                 seconds=1,
                                                 microseconds=1,
                                                 milliseconds=1,
                                                 minutes=1,
                                                 hours=1,
                                                 weeks=1)
        instance1_serialized = instance1.to_dict()
        import json

        instance1_as_str = json.dumps(instance1_serialized)
        instance1_from_str = json.loads(instance1_as_str)

        instance2 = SampleClass()
        instance2.from_dict(instance1_from_str)

        self.assertEqual(instance1.timedelta_property(),
                         instance2.timedelta_property())

    def test_description(self):
        description = SampleClass.get_description()
        self.assertIn('timedelta_property', description)
        # making sure it is json serializable
        import json

        self.assertIsNotNone(json.dumps(description))
