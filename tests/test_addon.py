import os
from unittest import TestCase
from xml.etree import ElementTree as ET
from xam import Addon
try:
    from collections import OrderedDict
except ImportError:
    from collective.ordereddict import OrderedDict


class TestAddon(TestCase):

    def test_parse(self):
        xml = ET.parse(os.path.join(os.path.dirname(__file__), 'data', 'addon.xml')).getroot()
        addon = Addon(xml)
        self.assertEqual('1.2.1', addon.version)
        self.assertEqual('plugin.video.academicearth', addon.id)
        self.assertEqual('Academic Earth', addon.name)
        self.assertEqual('Jonathan Beluch (jbel)', addon.provider)
        self.assertEqual({
            'xbmc.python': '2.0',
            'script.module.beautifulsoup': '3.0.8',
            'script.module.xbmcswift': '0.2.0',
            'plugin.video.youtube': '2.9.1',
        }, addon.dependencies)

        # TODO: better way to test this
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
