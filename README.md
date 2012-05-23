XBMC Addon Manager
==================

A CLI utility for searching and listing XBMC Addon Repositories.

Features
--------
* List addons available in remote repositories.
* List addons which require another addon as a dependency.
* Download the current version of an addon locally.
* Display the addon.xml for a remote addon.
* Search all addon.xml files in a repository for a given string.
* Supports the official XBMC respositories as well as 3rd party repos.


Installation
------------

    $ pip install xam


Example Usage
-------------

### List addon ids and versions for the Eden repo

    $ xam all
    * Updating addons.xml from remote...
    metadata.7176.com 1.0.9
    metadata.albums.1ting.com 1.0.7
    metadata.albums.allmusic.com 2.0.1
    ...
    webinterface.wtouch 0.4


### List addon id and version for every addon in bluecop's repo.

    $ xam --repo http://bluecop-xbmc-repo.googlecode.com/files/repository.bluecop.xbmc-plugins.zip all
    * Downloading http://bluecop-xbmc-repo.googlecode.com/files/repository.bluecop.xbmc-plugins.zip to /Users/jbeluch/.xam_cache/aHR0cDovL2JsdWVjb3AteGJtYy1yZXBvLmdvb2dsZWNvZGUuY29tL2ZpbGVzL3JlcG9zaXRvcnkuYmx1ZWNvcC54Ym1jLXBsdWdpbnMuemlw
    * Warning: Repositories which do not zip addons are unsupported at this time. The download functionality might not work properly.
    * Updating addons.xml from remote...
    plugin.video.amazon 0.4.6
    plugin.video.epix 0.1.0
    plugin.video.espn3 0.9.9
    plugin.video.free.cable 0.3.0
    plugin.video.hulu 3.4.5
    plugin.video.nba 0.0.3
    plugin.video.reddit.bc 0.0.3
    plugin.video.vevo 0.7.0
    plugin.video.yahoo.music.videos 0.0.3
    repository.bluecop.xbmc-plugins 1.0.1
    script.hululibraryautoupdate 1.1.2
    script.module.cryptopy 1.2.6
    script.module.demjson 1.4
    script.module.mechanize 0.2.5
    script.module.pycrypto 2.5


### Get the current version for the youtube plugin in the Dharma repo

    $ xam --repo dharma all | grep plugin.video.youtube
    plugin.video.youtube 2.1.4


### List all addons that require [xbmcswift][]
[xbmcswift]: https://github.com/jbeluch/xbmcswift 

    $ xam depends script.module.xbmcswift
    * Local addons.xml is up to date...
    plugin.audio.radioma 1.0
    plugin.video.myvideo_de 0.1.4
    plugin.video.academicearth 1.2.1
    plugin.video.khanacademy 1.4.2
    plugin.audio.radio_de 1.0.6
    plugin.video.aljazeera 0.9.0
    plugin.video.collegehumor 1.0.2
    plugin.video.4players 1.1.3
    plugin.video.eyetv.parser 2.1.1
    plugin.video.nasa 1.0.1
    plugin.video.wimp 1.0.0


### Search for any facebook related addons

    $ xam search facebook
    * Local addons.xml is up to date...
    script.web.viewer:1: Web viewer also allows addon developers to process application authorization (ie. facebook,flickr etc.) with little programming and without violating terms of use.
    script.facebook.media:1: <addon id="script.facebook.media" name="Facebook Media" provider-name="Rick Phillips (ruuk)" version="0.6.4">
    script.facebook.media:2:     <summary lang="en">Browse Facebook photos and videos</summary>


### Download a local copy of the youtube plugin

    $ xam get plugin.video.youtube
    * Local addons.xml is up to date...
    * Downloading http://mirrors.xbmc.org/addons/eden/plugin.video.youtube/fanart.jpg to plugin.video.youtube/fanart.jpg
    * Downloading http://mirrors.xbmc.org/addons/eden/plugin.video.youtube/changelog-2.9.1.txt to plugin.video.youtube/changelog-2.9.1.txt
    * Downloading http://mirrors.xbmc.org/addons/eden/plugin.video.youtube/plugin.video.youtube-2.9.1.zip to plugin.video.youtube/plugin.video.youtube-2.9.1.zip
    * Downloading http://mirrors.xbmc.org/addons/eden/plugin.video.youtube/icon.png to plugin.video.youtube/icon.png
    $ ls plugin.video.youtube/
    changelog-2.9.1.txt
    icon.png
    plugin.video.youtube-2.9.1.zip


### Show the addon.xml for the academic earth plugin
    
    $ xam info plugin.video.academicearth
    * Updating addons.xml from remote...
    Academic Earth (plugin.video.academicearth 1.2.1)
    -------------------------------------------------

    <addon id="plugin.video.academicearth" name="Academic Earth" provider-name="Jonathan Beluch (jbel)" version="1.2.1">
      <requires>
        <import addon="xbmc.python" version="2.0" />
        <import addon="script.module.beautifulsoup" version="3.0.8" />
        <import addon="script.module.xbmcswift" version="0.2.0" />
        <import addon="plugin.video.youtube" version="2.9.1" />
      </requires>
      <extension library="addon.py" point="xbmc.python.pluginsource">
        <provides>video</provides>
      </extension>
      <extension point="xbmc.addon.metadata">
        <platform>all</platform>
        <summary>Watch lectures from Academic Earth (http://academicearth.org)</summary>
        <description>Browse online courses and lectures from the world's top scholars.</description>
      </extension>
    </addon>

### List all addons for an XBMC installation

    $ cd ~/.xbmc/addons/
    $ xam freeze
    metadata.artists.allmusic.com==2.0.6
    metadata.common.allmusic.com==1.8.2
    metadata.common.hdtrailers.net==1.0.7
    skin.aeon.nox==2.0.0
    ...
    webinterface.wtouch==0.4

