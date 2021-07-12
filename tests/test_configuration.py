import unittest
import os, sys

p = os.path.abspath('.')
sys.path.insert(1, p)

from famapy.core.models import Configuration


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.config1 = Configuration({'F1': True, 'F2': False})
        self.config2 = Configuration({'F2': False, 'F1': True})
        self.config3 = Configuration({'F1': False, 'F2': True})
        self.config4 = Configuration({'F1': True, 'F2': False, 'F3': True})
        self.config5 = Configuration({'F1': True, 'F2': False, 'F3': False})

    def tearDown(self):
        pass

    def test_equals(self):
        self.assertEqual(self.config1, self.config2)
        self.assertNotEqual(self.config1, self.config3)
        self.assertNotEqual(self.config2, self.config3)
        self.assertNotEqual(self.config1, self.config4)
        self.assertNotEqual(self.config2, self.config4)
        self.assertNotEqual(self.config1, self.config5)
        self.assertNotEqual(self.config2, self.config5)

    def test_hash(self):
        self.assertEqual(hash(self.config1), hash(self.config2))
        self.assertNotEqual(hash(self.config1), hash(self.config3))
        self.assertNotEqual(hash(self.config2), hash(self.config3))
        self.assertNotEqual(hash(self.config1), hash(self.config4))
        self.assertNotEqual(hash(self.config2), hash(self.config4))
        self.assertNotEqual(hash(self.config1), hash(self.config5))
        self.assertNotEqual(hash(self.config2), hash(self.config5))


if __name__ == "__main__":
    unittest.main(verbosity=3)

