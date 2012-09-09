import unittest
try:
    from collections import OrderedDict
except ImportError:
    from collective.ordereddict import OrderedDict
from xam.cli.release import compare_versions


class TestRelease(unittest.TestCase):

    def test_compare_versions(self):
        known_values = [
            (('1.0', '1.1'), -1),
            (('1.1', '0.4'), 1),
            (('1.0', '1.0'), 0),
            (('0.0.1', '.1'), 0),
            (('0.0.0', '0'), 0),
            (('1', '0'), 1),
            (('.12', '.2'), 1),
            (('1.3', '1.3'), 0),
        ]
        for inp, expected in known_values:
            self.assertEqual(compare_versions(*inp), expected)


if __name__ == '__main__':
    unittest.main()
