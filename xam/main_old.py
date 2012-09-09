'''
    xam.xam
    ----------

    This module is the entry point for the console script xam.

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.
'''


USAGE = \
'''
    %(prog)s [options] {all, depends, get, info, search} [arg [arg ...]]

synopsis:
    %(prog)s all
    %(prog)s depends <plugin_id>
    %(prog)s get <plugin_id> [<plugin_id> ...]
    %(prog)s info <plugin_id>
    %(prog)s search <search_text>

commands:
    all
        Prints addon ids and current version numbers for every addon in the
        repo.

    depends
        Prints addon ids and current version for every addon which lists
        the specified addon id as a dependency.

    get
        Downloads the addon zip file and any assets to a folder in the
        current working directory. The folder name will be the addon id.

        NOTE: At this time, the download functionality will only work
        properly for repositories which zip their addons. Using this
        command for a repository which doesn't zip addons will definitely
        not download all of the necessary addon files.

    info
        Prints the specified addon's xml file to STDOUT.

    search
        Prints addon ids and matching lines for the provided text. A case
        insensitive seach of addon xml files is performed.

optional arguments:
    -r URL, --repo URL
        Either an official repo name [eden, eden_pre, dharma, dharma_pre]
        or a URL to a zipped repository file. Defaults to "eden". A list
        of 3rd party repos can be found here:
        http://wiki.xbmc.org/index.php?title=3rd_party_add-on_repositories

examples:
    %(prog)s --repo dharma all
        List addon id and version for every addon in the Dharma repo.

    %(prog)s --repo http://bluecop-xbmc-repo.googlecode.com/files/repository.bluecop.xbmc-plugins.zip all
        List addon id and version for every addon in bluecop's repo.

    %(prog)s depends script.module.xbmcswift
        List addon ids and version for every addon which lists
        script.module.xbmcswift as a dependency.

    %(prog)s get plugin.video.academicearth plugin.video.khanacademy
        Download the current versions of Acacdemic Earth and Khan Academy.

    %(prog)s info plugin.video.classiccinema
        Print addon.xml for the current Classic Cinema plugin.

    %(prog)s search lecture
        Print addon ids and matching lines for any addon containing the
        word lecture.
'''
