'''
    xam.addon
    ---------

    Contains the Addon class to represent an XBMC addon

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.

'''
from functools import wraps
from xml.etree import ElementTree as ET
try:
    from collections import OrderedDict
except ImportError:
    from collective.ordereddict import OrderedDict


def silence_attr_error(func):
    '''A decorator to allow a raised AttributeError to pass silently'''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError:
            return None
    return wrapper


# TODO: Extensions should parsed agnostically, and return an ordered dict
#       of extensions, queryable by the "point" attribute.
#       * A shortcut to metadata is acceptable

# TODO: For each extension, we need a list of attrs and child tags that
#       should be queryable.
class Addon(object):
    '''A class to hold information regarding an XBMC addon.'''

    def __init__(self, xml):
        '''Intializes an addon object for the provided addon xml'''
        self._xml = xml
        # These three properties are required, everything else is optional
        required_attrs = ['id', 'name', 'version']
        for attr in required_attrs:
            if attr not in self.xml.keys():
                raise Exception('Provided xml is missing the %s attribute' % attr)

    def __repr__(self):
        return '<Addon %s %s>' % (self.id, self.version)

    @property
    def xml(self):
        '''Retursn the root xml element for the addon'''
        return self._xml

    def to_xml_string(self):
        '''Returns a string containing the addon's xml'''
        return ET.tostring(self.xml, encoding='utf-8')

    def _get_version(self):
        '''Returns the addon's version'''
        return self.xml.get('version')

    def _set_version(self, version):
        '''Sets the addon's version'''
        self.xml.set('version', version)

    version = property(_get_version, _set_version)
    del _get_version, _set_version

    @property
    def id(self):
        '''Returns the addon's id'''
        return self.xml.get('id')

    @property
    def name(self):
        '''Returns the addon's name'''
        return self.xml.get('name')

    @property
    def provider(self):
        '''The addon's provider'''
        return self.xml.get('provider-name')

    @property
    def dependencies(self):
        '''A dict of required addons this addon is dependen on. Key is
        addon id and value is the required version.'''
        requires = self.xml.find('requires')
        if requires is not None:
            return dict((required.get('addon'), required.get('version'))
                    for required in requires.findall('import'))
        return {}

    #@property
    #def extensions(self):
        #extensions = self.xml.findall('extension')
        #if extensions:
            #return dict((ext.get('point')

    @property
    @silence_attr_error
    def metadata(self):
        '''The addon's metadata xml element'''
        return self.xml.find('./extension[@point="xbmc.addon.metadata"]')

    #@property
    #@silence_attr_error
    #def provides(self):
        #return self.pluginsource.find('provides').text

    @property
    @silence_attr_error
    def platform(self):
        '''The addon's platform'''
        return self.metadata.find('platform').text

    @property
    @silence_attr_error
    def summaries(self):
        '''Returns an OrderedDict of the addon's summaries. Key is an
        XBMC language code and value is the corresponding summary text.
        '''
        # TODO: figure out if we can default to en when no lang attr is present
        return OrderedDict((sum.get('lang'), sum.text) for sum in
                            self.metadata.findall('summary'))

    @silence_attr_error
    def summary(self, lang=None):
        '''Returns the summary for the provided language code or the
        first summary available if no language is provided. None is
        returned if there are no summaries available.
        '''
        if not lang:
            try:
                return self.summaries.values()[0]
            except IndexError:
                return None
        return self.summaries.get(lang)

    @property
    @silence_attr_error
    def descriptions(self):
        '''Returns an OrderedDict of the addon's descriptions. Key is
        an XBMC language code and value is the corresponding
        description text.'''
        return OrderedDict((sum.get('lang'), sum.text) for sum in
                            self.metadata.findall('description'))

    @silence_attr_error
    def description(self, lang=None):
        '''Returns the desciption for the provided language code or the
        first desciption available if no language is provided. None is
        returned if there are no descriptions available.
        '''
        if not lang:
            try:
                return self.descriptions.values()[0]
            except IndexError:
                return None
        return self.descriptions.get(lang)
