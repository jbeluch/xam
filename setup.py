'''
XBMC Addon Manager
------------------

A CLI utility for searching and listing XBMC Addon Repositories.

Setup
`````

::

    $ pip install xam
    $ xam --help

Links
`````

* `website <http://github.com/jbeluch/xam/>`_

'''
from setuptools import setup

setup(
    name='xam',
    version='0.1',
    url='http://github.com/jbeluch/xam/',
    license='BSD',
    author='Jonathan Beluch',
    author_email='web@jonathanbeluch.com',
    description='A utility for listing, searching and viewing source code for '
                'XBMC addons.',
    long_description=__doc__,
    packages=['xam'],
    platforms='any',
    install_requires=[
        'python>=2.7',
        'requests'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': [
            'xam = xam.xam:main'
        ]
    }
)
