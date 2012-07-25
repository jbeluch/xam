import os
from unittest import TestCase
from xml.etree import ElementTree as ET
from xam import Addon
try:
    from collections import OrderedDict
except ImportError:
    from collective.ordereddict import OrderedDict


class TestAddon(TestCase):

    def assert_attrs(self, obj, attrs):
        for attr_name, expected_value in attrs.items():
            attr_value = getattr(obj, attr_name)
            self.assertEqual(expected_value, attr_value)
            self.assertTrue(isinstance(attr_value, unicode))

    def assert_dict(self, expected, actual):
        for key, val in actual.items():
            self.assertTrue(isinstance(key, unicode))
            self.assertTrue(isinstance(val, unicode))
        self.assertEqual(expected, actual)

    def test_parse(self):
        addon = Addon.from_filename(os.path.join(os.path.dirname(__file__), 'data', 'addon.xml'))

        expected = {
            # attr_name: expected_value
            'version': u'1.2.1',
            'id': u'plugin.video.academicearth',
            'name': u'Academic Earth',
            'provider': u'Jonathan Beluch (jbel)',
        }
        self.assert_attrs(addon, expected)

        self.assert_dict({
            u'xbmc.python': u'2.0',
            u'script.module.beautifulsoup': u'3.0.8',
            u'script.module.xbmcswift': u'0.2.0',
            u'plugin.video.youtube': u'2.9.1',
        }, addon.dependencies)

        self.assertNotEqual(None, addon.metadata)
        self.assertEqual('all', addon.platform)
        self.assertEqual(OrderedDict(
            [(None, 'Watch lectures from Academic Earth (http://academicearth.org)')]
        ), addon.summaries)
        self.assertEqual('Watch lectures from Academic Earth (http://academicearth.org)',
                         addon.summary())
        #self.assertEqual('Watch lectures from Academic Earth (http://academicearth.org)',
                         #addon.summary('en'))
        self.assertEqual(OrderedDict(
            [(None,'Browse online courses and lectures from the world\'s top scholars.')]
        ), addon.descriptions)
        self.assertEqual('Browse online courses and lectures from the world\'s top scholars.',
                         addon.description())


    def test_setters(self):
        xml = ET.parse(os.path.join(os.path.dirname(__file__), 'data', 'addon.xml')).getroot()
        addon = Addon(xml)
        self.assertEqual('1.2.1', addon.version)
        addon.version = '1.2.2'
        self.assertEqual('1.2.2', addon.version)
