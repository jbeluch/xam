'''
    xam.repository
    --------------

    Contains the Repository class and some helper functions.
'''
import os
import sys
import base64
from zipfile import ZipFile
from urlparse import urljoin
from xml.etree import ElementTree as ET
import requests

from .common import urlretrieve
from .addon import Addon


def get(url):
    '''Returns a response for the given url.'''
    return requests.get(url).content


def safe_cache_fn(key):
    '''Returns an absolute path name for a cached file based on the
    provided key. The same file will always be returned for a given
    key.
    '''
    return cache_fn(base64.urlsafe_b64encode(key))


def cache_fn(filename):
    '''Returns an absolute filename in the xam cache folder for the
    given base filename.
    '''
    return os.path.join(os.getenv('HOME'), '.xam_cache', filename)


def write_file(filename, content):
    '''Writes content to filename'''
    with open(filename, 'w') as fileobj:
        fileobj.write(content)


class Repository(object):
    '''A class representing an XBMC addon repository.'''

    def __init__(self, info_url, datadir_url, checksum_url=None):
        '''If checksum_url is None, the remote addons.xml will be
        checked for every request. If provided, checksums will be
        verified to see if an update has occured.
        '''
        self.info_url = info_url
        self.checksum_url = checksum_url
        self.datadir_url = datadir_url
        if not self.datadir_url.endswith('/'):
            self.datadir_url = self.datadir_url + '/'
        self._remote_md5 = None
        self._local_md5 = None
        self._addons_xml = None
        self._addons = []
        self.xml = None
        self.parse_addons()

    @classmethod
    def from_zip(cls, zip_url):
        '''Returns a Repository instance for the provided zip_url.
        zip_url should be a url to a zipped repository file.
        '''
        # TODO: Download zip file to a temp location so it will be cleared
        filename = safe_cache_fn(zip_url)
        urlretrieve(zip_url, filename)

        # Attempt to extract the content addon.xml within the zip file
        zipfile = ZipFile(filename)
        try:
            addon_xml_filename = (filename for filename in zipfile.namelist()
                                  if filename.endswith('addon.xml')).next()
        except StopIteration:
            sys.exit('This repository doesn\'t appear to contain an addon.xml'
                     ' file.')

        # Parse the addon.xml and extract the three URLs
        with zipfile.open(addon_xml_filename) as addon_xml:
            xml = ET.parse(addon_xml)
        extension = xml.find('extension[@point="xbmc.addon.repository"]')
        info_url = extension.find('info').text
        checksum_url = extension.find('checksum').text
        datadir_url = extension.find('datadir').text

        # TODO: Add support for non-zipped addons
        if extension.find('datadir').get('zip') != True:
            print ('* Warning: Repositories which do not zip addons are '
                   'unsupported at this time. The download functionality might'
                   ' not work properly.')
        return cls(info_url, datadir_url, checksum_url)

    @property
    def addons_xml(self):
        '''Returns the current version of the repository's addons.xml
        as a string. If this repository has a checksum_url, we will
        attempt to use a cached version of addons.xml if the checksum
        is still valid.
        '''
        if self.remote_md5 is None or self.local_md5 != self.remote_md5:
            # Download everything
            print '* Updating addons.xml from remote...'
            self._addons_xml = get(self.info_url)
            if self.checksum_url is not None:
                # Some repos don't have a checksum URL, so we will have to
                # download them everytime
                write_file(safe_cache_fn(self.info_url), self._addons_xml)
                write_file(safe_cache_fn(self.checksum_url), self.remote_md5)
        elif self._addons_xml is None:
            print '* Local addons.xml is up to date...'
            with open(safe_cache_fn(self.info_url)) as addons_file:
                self._addons_xml = addons_file.read()
        return self._addons_xml

    @property
    def remote_md5(self):
        '''Returns the remote md5 checksum for a repository or None if
        the repository doesn't have a checksum url.
        '''
        if self.checksum_url is None:
            return None
        if self._remote_md5 is None:
            self._remote_md5 = get(self.checksum_url)
        return self._remote_md5

    @property
    def local_md5(self):
        '''Returns the md5 checksum of the local cached addons.xml or
        None if there is no cached copy.
        '''
        if self._local_md5 is None:
            try:
                with open(safe_cache_fn(self.checksum_url)) as checksum_file:
                    self._local_md5 = checksum_file.read()
            except IOError:
                return None
        return self._local_md5

    @property
    def addons(self):
        '''Returns a list of Addons for this repository'''
        return self._addons

    def parse_addons(self):
        '''Parses this repository's addons.xml file and creates Addon
        instances for each addon listed.'''
        self.xml = ET.fromstring(self.addons_xml)
        self._addons = [Addon(addon) for addon in self.xml.findall('addon')]

    def addon_data_urls(self, addon):
        '''Returns a dict of urls for the provided addons assets.

        Returned dict's keys are ['zip', 'icon', 'fanart', 'changelog']
        '''
        addon_dir = urljoin(self.datadir_url, '%s/' % addon.id)
        return {
            'zip': urljoin(addon_dir, '%s-%s.zip' % (addon.id, addon.version)),
            'icon': urljoin(addon_dir, 'icon.png'),
            'fanart': urljoin(addon_dir, 'fanart.jpg'),
            'changelog': urljoin(addon_dir,
                                 'changelog-%s.txt' % addon.version),
        }
