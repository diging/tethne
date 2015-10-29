import sys
sys.path.append('./')

import unittest

from tethne.utilities import _strip_punctuation

class TestStripPunctuation(unittest.TestCase):
    def test_str(self):
        self.assertEqual('asdf', _strip_punctuation('a.s,d;f?'))

    def test_unicode(self):
        self.assertEqual(u'asdf', _strip_punctuation(u'a.s,d;f?'))


if __name__ == '__main__':
    unittest.main()
