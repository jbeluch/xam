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

        self.assertEqual(addon.languages, ['en', 'fr'])
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


    def test_to_dict(self):
        addon = Addon.from_filename(os.path.join(os.path.dirname(__file__), 'data', 'addon.xml'))
        actual = addon.to_dict()

        with open(os.path.join(os.path.dirname(__file__), 'data', 'addon.xml')) as inp:
            xml = inp.read()
        expected = {
            'id': u'plugin.video.academicearth',
            'name': u'Academic Earth',
            'version': u'1.2.1',
            'provider': u'Jonathan Beluch (jbel)',
            'dependencies': {
                'xbmc.python': '2.0',
                'script.module.beautifulsoup': '3.0.8',
                'script.module.xbmcswift': '0.2.0',
                'plugin.video.youtube': '2.9.1',
            },
            'summaries': {None: u"Watch lectures from Academic Earth (http://academicearth.org)"},
            'descriptions': {None: u"Browse online courses and lectures from the world's top scholars."},
            'platform': 'all',
            '_xml': xml,
        }

        for key, val in expected.items():
            if not key.startswith('_'):
                self.assertEqual(val, actual[key])


LANG_XML_TMP = '''
<addon id="plugin.video.academicearth" name="Academic Earth" provider-name="Jonathan Beluch (jbel)" version="1.2.1">
  <extension point="xbmc.addon.metadata">
    %s
  </extension>
</addon>
'''
class TestLangTags(TestCase):

    def test_no_lang_tag(self):
        xmlstr = LANG_XML_TMP % ''
        addon = Addon(ET.fromstring(xmlstr))
        self.assertEqual(addon.languages, [])

    def test_self_close_lang_tag(self):
        xmlstr = LANG_XML_TMP % '<language/>'
        addon = Addon(ET.fromstring(xmlstr))
        self.assertEqual(addon.languages, [])

    def test_empty_lang_tag(self):
        xmlstr = LANG_XML_TMP % '<language></language>'
        addon = Addon(ET.fromstring(xmlstr))
        self.assertEqual(addon.languages, [])

    def test_data_lang_tag(self):
        xmlstr = LANG_XML_TMP % '<language>en</language>'
        addon = Addon(ET.fromstring(xmlstr))
        self.assertEqual(addon.languages, ['en'])

        xmlstr = LANG_XML_TMP % '<language>en fr</language>'
        addon = Addon(ET.fromstring(xmlstr))
        self.assertEqual(addon.languages, ['en', 'fr'])



if __name__ == '__main__':
   unittest.main()
