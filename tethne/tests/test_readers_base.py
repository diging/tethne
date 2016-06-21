import sys
sys.path.append('../tethne')

import unittest
from tethne.readers.base import FTParser, XMLParser
import xml.etree.ElementTree as ET

datapath = './tethne/tests/data/test.ft'
xmldatapath = './tethne/tests/data/dfr/citations.XML'


class TestXMLParser(unittest.TestCase):
    # def test_start(self):
    #     parser = XMLParser(xmldatapath, autostart=False)
    #     parser.start()
    #
    #     self.assertEqual(len(parser.data), 1,
    #                      'First data entry not instantiated.')
    #     self.assertIsInstance(parser.data[0], parser.entry_class)

    # def test_next(self):
    #     """
    #     ``next`` should return the first line of data.
    #     """
    #
    #     parser = XMLParser(xmldatapath)
    #     tag, data = parser.next()
    #     self.assertEqual(tag, 'doi')

    def test_handle(self):
        """
        ``handle`` should store the first line of data in the first data entry.
        """

        parser = XMLParser(xmldatapath)
        root = ET.parse(xmldatapath).getroot()
        elem = root.findall('.//doi')[0]
        tag, data = elem.tag, elem.text
        parser.handle(tag, data)

        self.assertEqual(len(parser.data), 1)
        self.assertTrue(hasattr(parser.data[0], tag),
                        'Data line not handled correctly. `{0}`'.format(tag) +
                        ' should be an attribute of the first data entry.')

    def test_parse(self):
        parser = XMLParser(xmldatapath)
        parser.parse()

        N = len(parser.data)
        
        self.assertEqual(N, 398, 'Expected 398 entries, found {0}'.format(N))


class TestFTParser(unittest.TestCase):
    def test_badpath(self):
        """
        If an invalid/non-existant path is passed to the constructor, should
        raise an ``IOError``.
        """

        with self.assertRaises(IOError):
            parser = FTParser('/this/path/doesnt/exist')
            parser

    def test_start(self):
        """
        Parser should advance to the first start tag, and instantiate the first
        data entry.
        """

        parser = FTParser(datapath, autostart=False)
        parser.start()

        self.assertEqual(parser.start_tag, parser.current_tag,
                         'Cannot identify start.')
        self.assertEqual(len(parser.data), 1,
                         'First data entry not instantiated.')
        self.assertIsInstance(parser.data[0], parser.entry_class)

    def test_next(self):
        """
        ``next`` should return the first line of data.
        """

        parser = FTParser(datapath)
        tag, data = parser.next()

        self.assertEqual(tag, 'FI')

    def test_handle(self):
        """
        ``handle`` should store the first line of data in the first data entry.
        """

        parser = FTParser(datapath)
        tag, data = parser.next()
        parser.handle(tag, data)

        self.assertEqual(len(parser.data), 1)
        self.assertTrue(hasattr(parser.data[0], tag),
                        'Data line not handled correctly. `{0}`'.format(tag) +
                        ' should be an attribute of the first data entry.')

    def test_parse(self):
        parser = FTParser(datapath)
        parser.parse()

        self.assertEqual(len(parser.data[0].TH), 3,
                         'Multi-line fields are not handled properly. Fields' +
                         ' with multiple lines should be parsed as a list or' +
                         ' array with one value per line.')

        N = len(parser.data)
        self.assertEqual(N, 2, 'Expected 2 data entries, found {0}'.format(N))


if __name__ == '__main__':
    unittest.main()
