'''
    xam.common
    ----------

    Contains some helpful functions with no other home.

    :copyright: (c) 2012 Jonathan Beluch
    :license: BSD, see LICENSE for more details.

'''
import requests


def urlretrieve(url, filename):
    '''Downloads the resource found at the remote url to the provided
    filename if the url returns an OK status.'''
    print '* Downloading %s to %s' % (url, filename)
    req = requests.get(url)
    if req.status_code == requests.codes.ok:
        with open(filename, 'wb') as output:
            output.write(req.content)
