from nio.modules.communication.matching.loose import LooseMatching
from nio.util.support.test_case import NIOTestCase

PUB_A_AND_B = {'type': ['A', 'B']}
PUB_TYPE_EMPTY = {'type': []}
PUB_A_ONLY = {'type': ['A']}
PUB_C_ONLY = {'type': ['C']}
PUB_C_AND_TEST = {'type': ['C'], 'flag': ['test']}

SUB_A_ONLY = {'type': ['A']}
SUB_B_ONLY = {'type': ['B']}
SUB_A_AND_B = {'type': ['A', 'B']}
SUB_TYPE_EMPTY = {'type': []}
SUB_TEST_ONLY = {'flag': 'test'}
SUB_A_B_AND_TEST = {'type': ['A', 'B'], 'flag': ['test']}


class TestLooseMatching(NIOTestCase):
    def test_default_matching_scenario2(self):
        # differ from default, expected
        self.assertTrue(LooseMatching.matches(SUB_A_ONLY, PUB_A_AND_B))
        # differ from default, expected
        self.assertTrue(LooseMatching.matches(SUB_B_ONLY, PUB_A_AND_B))

        self.assertTrue(LooseMatching.matches(SUB_A_AND_B, PUB_A_AND_B))
        self.assertTrue(LooseMatching.matches(SUB_A_AND_B, PUB_A_ONLY))

        self.assertTrue(LooseMatching.matches(SUB_TYPE_EMPTY, PUB_A_ONLY))
        self.assertTrue(LooseMatching.matches(SUB_A_ONLY, PUB_TYPE_EMPTY))
        self.assertTrue(LooseMatching.matches(SUB_TYPE_EMPTY, PUB_TYPE_EMPTY))
        self.assertTrue(LooseMatching.matches({}, {}))

        self.assertFalse(LooseMatching.matches(SUB_A_AND_B, PUB_C_ONLY))
        self.assertTrue(LooseMatching.matches(SUB_TEST_ONLY, PUB_C_AND_TEST))
        self.assertFalse(LooseMatching.matches(SUB_A_B_AND_TEST,
                                               PUB_C_AND_TEST))
