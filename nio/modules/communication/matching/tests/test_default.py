from nio.modules.communication.matching.default import DefaultMatching
from nio.testing.test_case import NIOTestCase

Pub_A = {'type': ['A'], "source": ['C']}
Pub_B = {'type': ['A'], "source": ['D']}
Pub_C = {'type': ['B'], "source": ['D']}
Pub_D = {'type': ['A'], "source": ['E']}
Pub_E = {'type': ['B'], "source": ['F']}
Pub_F = {'type': ['A'], "source": ['C', 'G']}

Sub_A = {'type': ['A']}
Sub_B = {'type': ['A'], 'source': ['C', 'D']}
Sub_C = {'source': ['D']}
Sub_D = {'type': ['B'], 'source': ['E']}
Sub_E = {'non_pub_key': ['G']}
Sub_F = {'type': ['A'], 'non_pub_key': ['C']}


class TestDefaultMatching(NIOTestCase):
    def test_default_matching_scenario1(self):
        self.assertTrue(DefaultMatching.matches(Sub_A, Pub_A))
        self.assertTrue(DefaultMatching.matches(Sub_A, Pub_B))
        self.assertFalse(DefaultMatching.matches(Sub_A, Pub_C))
        self.assertTrue(DefaultMatching.matches(Sub_A, Pub_D))
        self.assertFalse(DefaultMatching.matches(Sub_A, Pub_E))
        self.assertTrue(DefaultMatching.matches(Sub_A, Pub_F))

        self.assertTrue(DefaultMatching.matches(Sub_B, Pub_A))
        self.assertTrue(DefaultMatching.matches(Sub_B, Pub_B))
        self.assertFalse(DefaultMatching.matches(Sub_B, Pub_C))
        self.assertFalse(DefaultMatching.matches(Sub_B, Pub_D))
        self.assertFalse(DefaultMatching.matches(Sub_B, Pub_E))
        # a no match since publisher is offering 'G' as well.
        self.assertFalse(DefaultMatching.matches(Sub_B, Pub_F))

        self.assertFalse(DefaultMatching.matches(Sub_C, Pub_A))
        self.assertTrue(DefaultMatching.matches(Sub_C, Pub_B))
        self.assertTrue(DefaultMatching.matches(Sub_C, Pub_C))
        self.assertFalse(DefaultMatching.matches(Sub_C, Pub_D))
        self.assertFalse(DefaultMatching.matches(Sub_C, Pub_E))
        self.assertFalse(DefaultMatching.matches(Sub_C, Pub_F))

        self.assertFalse(DefaultMatching.matches(Sub_D, Pub_A))
        self.assertFalse(DefaultMatching.matches(Sub_D, Pub_B))
        self.assertFalse(DefaultMatching.matches(Sub_D, Pub_C))
        self.assertFalse(DefaultMatching.matches(Sub_D, Pub_D))
        self.assertFalse(DefaultMatching.matches(Sub_D, Pub_E))

        self.assertFalse(DefaultMatching.matches(Sub_E, Pub_A))
        self.assertFalse(DefaultMatching.matches(Sub_E, Pub_B))
        self.assertFalse(DefaultMatching.matches(Sub_E, Pub_C))
        self.assertFalse(DefaultMatching.matches(Sub_E, Pub_D))
        self.assertFalse(DefaultMatching.matches(Sub_E, Pub_E))
        self.assertFalse(DefaultMatching.matches(Sub_E, Pub_F))

        self.assertFalse(DefaultMatching.matches(Sub_F, Pub_A))
        self.assertFalse(DefaultMatching.matches(Sub_F, Pub_B))
        self.assertFalse(DefaultMatching.matches(Sub_F, Pub_C))
        self.assertFalse(DefaultMatching.matches(Sub_F, Pub_D))
        self.assertFalse(DefaultMatching.matches(Sub_F, Pub_E))
        self.assertFalse(DefaultMatching.matches(Sub_F, Pub_F))
