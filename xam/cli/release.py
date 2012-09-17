'''
    xam.release
    -----------

    Contains the release script to automate the release process for an XBMC
    addon.

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.
'''
import re
import os
import sys
from subprocess import check_call, check_output
import logging

from cliff.command import Command
from colorama import init
init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint, colored

from xam.addon import Addon
from xam.repository import get_repo
from xam.cli import REPO_NAMES, add_repo_arg




BLUE = lambda text: colored(text, 'blue')
GREEN = lambda text: colored(text, 'green')
RED = lambda text: colored(text, 'red')

def bump_minor(version_str):
    '''Given a version string, increments the right-most number by 1 and
    returns the new value.

    >>> bump_minor('1.2.3')
    '1.2.4'
    '''
    left, right = version_str.rsplit('.', 1)
    right = int(right) + 1
    return '%s.%s' % (left, right)


def compare_versions(version_a, version_b):
    '''Compares two versions strings and returns 1 if version_a is greater, -1
    is version_b is greater or 0 if they are equal.

    >>> compare_versions('1.0', '1.1')
    -1
    >>> compare_versions('1.1', '0.4')
    1
    >>> compare_versions('0.0.1', '.1')
    0
    '''
    if version_a == version_b:
        return 0

    # Convert parts to ints and strip out blank parts:
    # '.1'.split('.') will result in ['', '1']
    aparts = [int(part) for part in version_a.split('.') if part]
    bparts = [int(part) for part in version_b.split('.') if part]

    # if part lengths are unequal prepend with zeros
    if len(aparts) > len(bparts):
        bparts = [0] * (len(aparts) - len(bparts)) + bparts
    elif len(bparts) > len(aparts):
        aparts = [0] * (len(bparts) - len(aparts)) + aparts

    # same number of parts now, start comparing from leftmost part
    for a, b in zip(aparts, bparts):
        if a > b:
            return 1
        elif b > a:
            return -1
    # the only way we can get here, is if the versions strings aren't equal,
    # but when prepended with zeros they are equal. e.g.: .1 and 0.0.1
    return 0


def write_file(path, contents):
    '''Writes the given contents to the given path'''
    with open(path, 'w') as out:
        out.write(contents)


def generate_email_output(addon_id, version, git_url, tag, xbmc_version):
    '''Prints the message body for a mailing list email.'''
    lines = [
        '',
        '+--------------------+',
        '| Mailing List Email |',
        '+--------------------+',
        '',
        'To: xbmc-addons@lists.sourceforge.net',
        'Subject: [git pull] %s' % addon_id,
        '',
        '*addon - %s' % addon_id,
        '*version - %s' % version,
        '*url - %s' % git_url,
        '*tag - %s' % tag,
        '*xbmc version - %s' % xbmc_version,
        '',
        '',
    ]
    return lines


class ReleaseAddon(Command):
    '''Release a new verison of an addon'''

    log = logging.getLogger(__name__)

    def exit_if_negative(self, msg):
        if not self.yes_no(msg):
            raise RuntimeError('Aborting.')

    def yes_no(self, msg):
        '''Returns False if user entered n or N, True otherwise'''
        ans = raw_input(msg + ' (Y/n) ')
        return ans not in ['N', 'n']
        

    def prompt(self, msg, default=None):
        '''Prints a message and gathers input from the user. The provided default
        is returned if the user provides no input.
        '''
        if default is not None:
            msg = '%s [%s] ' % (msg, default)
        else:
            msg += ': '
        ans = raw_input(msg)
        if ans is not None and len(ans) > 0:
            return ans
        return default

    def get_parser(self, prog_name):
        parser = super(ReleaseAddon, self).get_parser(prog_name)
        add_repo_arg(parser)
        return parser

    def get_cwd_addon(self):
        '''Returns a xam.Addon object for the current addon. Aborts the script
        if no addon.xml file can be found in the current working directory.
        '''
        try:
            return Addon.from_filename('addon.xml')
        except IOError:
            raise RuntimeError('Could not find addon.xml in the current '
                               'directory. Run this script from the root '
                               'directory of your addon.')

    def update_dependencies(self, addon_to_release, xbmc_version):
        '''For any required dependencies, attempts to to update the version number
        to the newest version available in the XBMC official repository.
        '''
        repo = get_repo(xbmc_version)
        addons = repo.addons
        for addon_id, addon_version in addon_to_release.dependencies.items():
            if addon_id != 'xbmc.python':  # skip python dependency
                try:
                    addon = (addon for addon in repo.addons if addon.id == addon_id).next()
                except StopIteration:
                    # ERROR: no addon with that id
                    sys.exit('You have a dependency listed on "%s" but I can\'t '
                             'find an addon with that ID in the %s repository. '
                             'Aborting.' % (addon_id, xbmc_version))

                if compare_versions(addon_version, addon.version) > 0:
                    # ERROR: newest version available is < specified version
                    sys.exit('You require version %s for addon %s, but the newest '
                             'version I can find in the repository is %s. '
                             'Aborting.' % (addon_version, addon_id,
                                            addon.version))
                elif compare_versions(addon_version, addon.version) < 0:
                    # found newer version, prompt for update
                    msg = ('[?] There is a newer version of %s available. '
                           'Would you like to update the dependency from %s to'
                           ' %s?' % (BLUE(addon_id), BLUE(addon_version),
                                     BLUE(addon.version)))
                    if self.yes_no(msg):
                        self.app.stdout.write('Writing to addon.xml...')
                        addon_to_release.set_dependency_version(addon_id, addon.version)
                        write_file('addon.xml', addon_to_release.to_xml_string())
                        self.app.stdout.write(GREEN('OK') + '\n')
                else:
                    msg = 'Dependency %s is already at the newest version.\n' % BLUE(addon_id)
                    self.app.stdout.write(msg)

    def take_action(self, parsed_args):
        '''Performs a release of an XBMC addon.'''
        # Parse addon.xml
        addon = self.get_cwd_addon()
        reponame = parsed_args.repo

        # determine local git branch
        current_branch = check_output('git symbolic-ref HEAD 2>/dev/null',
                                      shell=True)
        if current_branch is None or not current_branch.startswith('refs/heads/'):
            raise RuntimeError('Could not determine current git branch.')
        current_branch_trimmed = current_branch.replace('refs/heads/', '').strip()

        lines = [
            '',
            '''  oooo    ooo  .oooo.   ooo. .oo.  .oo.''',
            '''   `88b..8P'  `P  )88b  `888P"Y88bP"Y88b''',
            '''     Y888'     .oP"888   888   888   888''',
            '''   .o8"'88b   d8(  888   888   888   888''',
            '''  o88'   888o `Y888""8o o888o o888o o888o''',
            '',
            '''           (XBMC ADDON MANAGER)''',
            '',
            '  I\'m going to help you create a new release for %s.' % BLUE(addon.name),
            '',
            '.. Init ..',
            '',
            'Please answer the following:',
            '',
        ]   
        self.app.stdout.write('\n'.join(lines))
        
        # Verify current branch
        msg = '[?] I see you are using git. Is %s the branch you want to use for the release?' % BLUE(current_branch_trimmed)
        self.exit_if_negative(msg)

        # Verify xbmc_version
        msg = '[?] This release will be for XBMC %s. Is this correct?' % BLUE(reponame)
        self.exit_if_negative(msg)

        # Check for dirty repo
        is_dirty = check_output('git status --porcelain', shell=True)
        if is_dirty:
            msg = ('[?] Your git working directory has uncommitted changes. '
                   'These changes will be included in the release commit. '
                   'Would you like to continue anyway?')
            self.exit_if_negative(msg)

        # TODO
        '  * You are using a `git remote` named "origin".',

        # Now onto the release setup
        lines = [
            '',
            '.. Release Metadata for %s ..' % BLUE(addon.id),
            '',
        ]
        self.app.stdout.write('\n'.join(lines) + '\n')

        # version
        msg = '[?] The current version is %s. What should the new version be?' % BLUE(addon.version)
        new_version = self.prompt(msg, default=bump_minor(addon.version))
        addon.version = new_version
        self.app.stdout.write('Writing new version to addon.xml...')
        write_file('addon.xml', addon.to_xml_string())
        self.app.stdout.write(GREEN('OK') + '\n')
    
        # Check dependencies
        if len(addon.dependencies) > 1:
            msg = '[?] I see your addon has a few dependencies. Would you like to check for new versions?'
            if self.yes_no(msg):
                self.update_dependencies(addon, reponame)

        if os.path.exists('changelog.txt'):
            msg = '[?] I see you have a %s. Would you like to update it now?' % BLUE('changelog.txt')
            if self.yes_no(msg):
                check_call([os.getenv('EDITOR'), 'changelog.txt'])

        # Final ok
        msg = '[?] I\'m ready to commit the changes and tag the release. Should we continue?'
        self.exit_if_negative(msg)

        lines = [
            '',
            '.. Release %s..' % BLUE(addon.version),
            '',
        ]
        self.app.stdout.write('\n'.join(lines) + '\n')
    
        # git add -A .
        self.app.stdout.write('Adding local changes to staging...')
        check_call('git add -A', shell=True)
        self.app.stdout.write(GREEN('OK') + '\n')

        # write commit message
        self.app.stdout.write('Creating commit...')
        check_call('git commit -m "[xam-release-script] creating release for'
                   ' version %s"' % new_version, shell=True)
        self.app.stdout.write(GREEN('OK') + '\n')

        # git tag release
        self.app.stdout.write('Tagging release...')
        check_call('git tag -a "%s" -m "%s v%s"' % (new_version, reponame,
                                                         new_version), shell=True)
        self.app.stdout.write(GREEN('OK') + '\n')

        # git push
        self.app.stdout.write('Pushing commit and tags to remote...')
        check_call('git push && git push --tags', shell=True)
        self.app.stdout.write(GREEN('OK') + '\n')

        msg = GREEN('Congrats. Release was successful.')
        self.app.stdout.write('\n' + msg + '\n')

        # attempt to guess public repo URL if using github...  push_url = '<INSERT_REPO_URL>'
        output = check_output('git remote -v | grep origin | grep push | cut -f1'
                              ' -d" "', shell=True)
        match = re.match(r'origin\tgit@github.com:(.+?\.git)', output)
        push_url = RED('<YOUR REPO URL>')
        if match is not None:
            push_url = 'git://github.com/%s' % match.group(1)

        # print email
        output = generate_email_output(addon.id, addon.version, push_url, addon.version,
                    reponame.lower())
        self.app.stdout.write('\n'.join(output))
