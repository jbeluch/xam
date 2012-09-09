'''
    xam.release
    -----------

    Contains the release script to automate the release process for an XBMC
    addon.

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.
'''
import re
import sys
from subprocess import check_call, check_output
from .addon import Addon
from .repository import get_repo


def prompt(msg, default=None):
    '''Prints a message and gathers input from the user. The provided default
    is returned if the user provides no input.
    '''
    if default is not None:
        msg = '%s [%s]: ' % (msg, default)
    else:
        msg += ': '
    ans = raw_input(msg)
    if ans is not None and len(ans) > 0:
        return ans
    return default


def get_addon():
    '''Returns a xam.Addon object for the current addon. Aborts the script if
    no addon.xml file can be found in the current working directory.
    '''
    try:
        return Addon.from_filename('addon.xml')
    except IOError:
        sys.exit('Could not find addon.xml in the current directory.'
                 ' Run this script from the root directory of your addon.'
                 ' Aborting.')


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


def print_email(addon_id, version, git_url, tag, xbmc_version):
    '''Prints the message body for a mailing list email.'''
    lines = [
        'Mailing List Email',
        '------------------',
        '',
        'Subject: [git pull] %s' % addon_id,
        '*addon - %s' % addon_id,
        '*version - %s' % version,
        '*url - %s' % git_url,
        '*tag - %s' % tag,
        '*xbmc version - %s' % xbmc_version,
        '',
        '',
    ]

    for line in lines:
        print line

def update_dependencies(addon_to_release, xbmc_version):
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
                ans = prompt('I found a newer version of %s in the repository. '
                             'Would you like to update the dependency from '
                             'version %s to version %s? y/n.' % (
                                addon_id, addon_version, addon.version),
                             default='y')
                if ans == 'y':
                    print 'Updating %s to version %s' % (addon_id, addon.version)
                    addon_to_release.set_dependency_version(addon_id, addon.version)
            else:
                print 'Dependency %s is already at the newest version.' % addon_id


def release(args):
    '''Performs a release of an XBMC addon.'''
    # Parse addon.xml
    addon = get_addon()
    xbmc_version = args.args[0]

    # determine local git branch
    current_branch = check_output('git symbolic-ref HEAD 2>/dev/null',
                                  shell=True)
    if current_branch is None or not current_branch.startswith('refs/heads/'):
        sys.exit('Could not determine current git branch. Aborting.')
    current_branch_trimmed = current_branch.replace('refs/heads/', '')

    lines = [
        '',
        '** Creating new %s release for XBMC version %s. **' % (addon.id,
                                                                xbmc_version),
        '',
        'Assumptions:',
        '  * The current working directory is the root of your addon.',
        '  * You are using git for your addon.',
        '  * You are using a `git remote` named "origin".',
        '  * The current checked out git branch is the one you want to use.',
        '  * Your git working directory is clean (any local changes will be'
        ' committed).',
        '',
        'What this script will do:',
        '  1. Update the version attribute of the <addon> tag in addon.xml'
        ' (user will be prompted for new version number).',
        '  2. The script will pause to allow you to update your changelog.txt',
        '  3. Create a commit using `git add -A`. This will include the'
        ' addon.xml and any other changed file, e.g. changelog.txt',
        '  4. Tag the release using the version number.',
        '  5. Push the current brach and tags to the git-remote named origin.',
        '',
    ]
    print '\n'.join(lines)

    ans = prompt('If any of these assumptions are not true, please enter "q"'
                 ' to quit. Otherwise,  hit Enter to continue.')
    if ans == 'q':
        sys.exit()

    # Check dependencies
    ans = prompt('Would you like to check for newer versions of depdencies '
                 '(y/n)?', default='y')
    if ans == 'y':
        update_dependencies(addon, xbmc_version)

    # Ask for new version
    new_version = prompt('Specify new version number',
                         default=bump_minor(addon.version))
    addon.version = new_version
    write_file('addon.xml', addon.to_xml_string())

    # Pause and allow user to update changelog.txt
    print 'Now would be a good time to update your changelog.txt.'
    prompt('Go ahead, I\'ll wait. Hit Enter when you\'re ready to continue.')

    # git add -A .
    prompt('Ok, now I\'m going to execute `git add -A`')
    check_call('git add -A', shell=True)

    # write commit message
    prompt('Now let\'s commit these changes')
    check_call('git commit -m "[xam-release-script] creating release for'
               ' version %s"' % new_version, shell=True)

    # git tag release
    prompt('Creating tag %s' % new_version)
    check_call('git tag -a "%s" -m "%s v%s"' % (new_version, xbmc_version,
                                                     new_version), shell=True)

    # git push
    prompt('Now pushing new commit and new tag to remote')
    check_call('git push && git push --tags', shell=True)

    print
    print 'Congrats. Release was successful. See mailing list email below.'
    print

    # attempt to guess public repo URL if using github...
    push_url = '<INSERT_REPO_URL>'
    output = check_output('git remote -v | grep origin | grep push | cut -f1'
                          ' -d" "', shell=True)
    match = re.match(r'origin\tgit@github.com:(.+?\.git)', output)
    if match is not None:
        push_url = 'git://github.com/%s' % match.group(1)

    # print email
    print_email(addon.id, addon.version, push_url, addon.version,
                xbmc_version.lower())
