'''
    xam.extensions
    --------------

    Contains an up to date list of XBMC extension points and their
    respective attributes and child tag names.

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.
'''


EXTENSIONS = {
    # extension_name: ([extension_attrs], [extension_children_tag_names])
    'xbmc.gui.skin': ([], []),
    'xbmc.gui.webinterface': ([], []),
    'xbmc.addon.repository': ([], []),
    'xbmc.service': (['library', 'start'], []),
    'xbmc.metadata.scraper.albums': ([], []),
    'xbmc.metadata.scraper.artists': ([], []),
    'xbmc.metadata.scraper.movies': ([], []),
    'xbmc.metadata.scraper.musicvideos': ([], []),
    'xbmc.metadata.scraper.tvshows': ([], []),
    'xbmc.metadata.scraper.library': ([], []),
    'xbmc.ui.screensaver': ([], []),
    'xbmc.player.musicviz': ([], []),
    'xbmc.python.pluginsource': (['library'], []),
    'xbmc.python.script': ([], []),
    'xbmc.python.weather': ([], []),
    'xbmc.python.subtitles': ([], []),
    'xbmc.python.lyrics': ([], []),
    'xbmc.python.library': ([], []),
    'xbmc.python.module': ([], []),
    'xbmc.addon.video': ([], []),
    'xbmc.addon.audio': ([], []),
    'xbmc.addon.image': ([], []),
}
