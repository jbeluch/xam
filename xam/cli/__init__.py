import os
import logging
from urllib import urlretrieve
from cliff.command import Command
from xam import repos
from xam.repository import get_repo


REPO_NAMES = [attr for attr in repos.__dict__.keys()
              if not attr.startswith('_')]


def uppercase(inp):
    return inp.upper()


def add_repo_arg(parser):
    parser.add_argument('--repo', type=uppercase, choices=REPO_NAMES,
                        default='FRODO')


def generate_addon_output(addon):
    title = '%s (%s %s)' % (addon.name, addon.id, addon.version)
    lines = [
        title,
        '-' * len(title),
        addon.to_xml_string(),
    ]
    return '\n'.join(lines)


class ListAddons(Command):
    '''List addon id and addon version for every addon in the provided
    repo.
    '''

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ListAddons, self).get_parser(prog_name)
        add_repo_arg(parser)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('Showing addon ids and versions for %s repo.'
                      % parsed_args.repo)

        repo = get_repo(parsed_args.repo)
        for addon in sorted(repo.addons, key=lambda addon: addon.id):
            self.app.stdout.write('%s %s\n' % (addon.id, addon.version))



class ShowAddonInfo(Command):
    '''Shows the contents of addon.xml for the provided addon id.'''

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowAddonInfo, self).get_parser(prog_name)
        add_repo_arg(parser)
        parser.add_argument('addon_id')
        return parser

    def take_action(self, parsed_args):
        addonid = parsed_args.addon_id
        reponame = parsed_args.repo

        self.log.debug('Showing info for %s in %s' % (addonid, reponame))

        repo = get_repo(reponame)
        try:
            addon = (addon for addon in repo.addons
                     if addon.id == addonid).next()
        except StopIteration:
            raise RuntimeError('No addon found with id %s' % addonid)

        self.app.stdout.write(generate_addon_output(addon))



class ShowDependentAddons(Command):
    '''Returns a list of addon id/versions which list the specified
    addon as a dependency.
    '''

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ShowDependentAddons, self).get_parser(prog_name)
        add_repo_arg(parser)
        parser.add_argument('addon_id')
        return parser

    def take_action(self, parsed_args):
        addonid = parsed_args.addon_id
        reponame = parsed_args.repo

        self.log.debug('Listing dependent addons for info for %s in %s'
                       % (addonid, reponame))

        repo = get_repo(reponame)
        dependents = [addon for addon in repo.addons
                      if addonid in addon.dependencies.keys()]

        for addon in dependents:
            self.app.stdout.write('%s %s\n' % (addon.id, addon.version))


class GetAddon(Command):
    '''For the provided addon ids, attempts to download the zipped
    addon, fanart.jpg, icon.png and changelog.txt. All downloaded files
    are located in a directory within the current working directory
    named after the addon id.
    '''

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(GetAddon, self).get_parser(prog_name)
        add_repo_arg(parser)
        parser.add_argument('addon_id', nargs='+')
        return parser

    def take_action(self, parsed_args):
        addonids = parsed_args.addon_id
        reponame = parsed_args.repo

        repo = get_repo(reponame)
        addons = [addon for addon in repo.addons if addon.id in addonids]
        data_urls = [repo.addon_data_urls(addon) for addon in addons]

        for addon, urls in zip(addons, data_urls):
            addonids.remove(addon.id)
            self.log.info('Downloading %s from %s to %s'
                          % (addon.id, reponame, addon.id))

            try:
                os.mkdir(addon.id)
            except OSError:
                raise RuntimeError('* Cannot make directory %s. If it exists, '
                                   'try removing it and running again.'
                                   % addon.id)

            for _, url in urls.items():
                filename = os.path.join(addon.id, url.rsplit('/', 1)[1])
                self.log.debug('Downloading %s to %s' % (url, filename))
                urlretrieve(url, filename)

        for addonid in addonids:
            # we couldn't find an addon with that id
            self.log.warning("Couldn't find %s in %s" % (addonid, reponame))



class SearchAddons(Command):
    '''Does a case insensitive (and xml ignorant) search of all addons'
    addon.xml file and lists matches.
    '''

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(SearchAddons, self).get_parser(prog_name)
        add_repo_arg(parser)
        parser.add_argument('search_term')
        return parser

    def take_action(self, parsed_args):
        reponame = parsed_args.repo
        search_term = parsed_args.search_term

        self.log.debug('Searching for %s in %s' % (search_term, reponame))

        repo = get_repo(reponame)
        text = search_term.lower()

        for addon in repo.addons:
            if text in addon.to_xml_string():
                lines = addon.to_xml_string().splitlines()
                matching_lines = [line for line in lines if text in line.lower()]
                for i, line in enumerate(matching_lines):
                    self.app.stdout.write('%s:%d: %s\n' % (addon.id, i + 1,
                                                         line))
