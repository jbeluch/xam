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
    check_call('git push --tags origin', shell=True)

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
