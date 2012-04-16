'''
    xam.xam
    ----------

    This module is the entry point for the console script xam.

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.
'''
import os
import sys
import argparse

import repos
from .repository import Repository
from .common import urlretrieve


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
        or a URL to a zipped repository file. Defaults to "eden". (A list
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


def parse_cli():
    '''Parses the command line and returns a tuple of
    (command, args)
    '''
    parser = argparse.ArgumentParser(description='Search XBMC addons.',
                                     usage=USAGE)
    parser.add_argument('-r', '--repo', default='eden')
    parser.add_argument('command')
    parser.add_argument('args', nargs='*')
    args = parser.parse_args()

    if args.command not in ['search', 'info', 'depends', 'get', 'all']:
        parser.error('Invalid command')

    # All commands require at least 1 arg except for all
    if args.command != 'all' and len(args.args) == 0:
        parser.error('Too few args')

    if args.command == 'all' and len(args.args) > 0:
        parser.error('Too many args.')

    # Everything except get takes only 1 arg
    if args.command in ['search', 'info', 'depends'] and len(args.args) > 1:
        parser.error('Too many args.')

    return args.command, args


def get_repo(name_or_url):
    '''Returns a repository for a given name or url. name_or_url can be
    an official repository name found in repos.py or it can be a url to
    a zipped repository file.
    '''
    if hasattr(repos, name_or_url.upper()):
        return Repository(*getattr(repos, name_or_url.upper()))
    else:
        return Repository.from_zip(name_or_url)


def all_addons(args):
    '''List addon id and addon version for every addon in the provided
    repo.
    '''
    repo = get_repo(args.repo)
    for addon in sorted(repo.addons, key=lambda addon: addon.id):
        print addon.id, addon.version


def info(args):
    '''Shows the contents of addon.xml for the provided addon id.'''
    addonid = args.args[0]
    repo = get_repo(args.repo)
    try:
        addon = (addon for addon in repo.addons if addon.id == addonid).next()
    except StopIteration:
        sys.exit('No addon found with id %s' % addonid)
    print_addon(addon, detailed=True)


def depends(args):
    '''Returns a list of plugin id/versions which list the specified
    addon as a dependency.
    '''
    addonid = args.args.pop(0)
    repo = get_repo(args.repo)
    dependents = [addon for addon in repo.addons
                  if addonid in addon.dependencies.keys()]
    print_addons(dependents)


def search(args):
    '''Does a case insensitive (and xml ignorant) search of all addons'
    addon.xml file and lists matches.
    '''
    text = args.args.pop(0).lower()
    repo = get_repo(args.repo)

    for addon in repo.addons:
        if text in addon.to_xml_string():
            lines = addon.to_xml_string().splitlines()
            matching_lines = [line for line in lines if text in line.lower()]
            for i, line in enumerate(matching_lines):
                print '%s:%d: %s' % (addon.id, i + 1, line)


def get(args):
    '''For the provided addon ids, attempts to download the zipped
    addon, fanart.jpg, icon.png and changelog.txt. All downloaded files
    are located in a directory within the current working directory
    named after the addon id.
    '''
    pluginids = args.args
    repo = get_repo(args.repo)
    addons = [addon for addon in repo.addons if addon.id in pluginids]
    data_urls = [repo.addon_data_urls(addon) for addon in addons]

    for addon, urls in zip(addons, data_urls):
        try:
            os.mkdir(addon.id)
        except OSError:
            sys.exit('* Cannot make directory for %s. If it exists, try'
                     ' removing it and running again.' % addon.id)
        for _, url in urls.items():
            urlretrieve(url, os.path.join(addon.id, url.rsplit('/', 1)[1]))


def print_addons(addons, detailed=False):
    '''Prints a list of addons to STDOUT'''
    for addon in addons:
        print_addon(addon, detailed)


def print_addon(addon, detailed=False):
    '''Prints  an addon to STDOUT.

    If detailed is False, the format is 'addon_id addon_version'.

    If detailed is True, the addon name, id and version are printed
    along with the addon's xml file.
    '''
    if not detailed:
        print addon.id, addon.version
    else:
        print '%s (%s %s)' % (addon.name, addon.id, addon.version)
        print '-' * len('%s (%s %s)' % (addon.name, addon.id, addon.version))
        print
        print addon.to_xml_string()


def main():
    '''Dispatches to the proper method based on CLI arguments.'''
    command, args = parse_cli()
    dispatcher = {
        'all': all_addons,
        'info': info,
        'depends': depends,
        'get': get,
        'search': search,
    }

    # Set up .xam_cache folder
    try:
        os.mkdir(os.path.join(os.getenv('HOME'), '.xam_cache'))
    except OSError:
        pass

    dispatcher[command](args)
