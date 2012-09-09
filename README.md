XBMC Addon Manager
==================

[![Build Status](https://secure.travis-ci.org/jbeluch/xam.png)](http://travis-ci.org/jbeluch/xam)

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

### Release a new version of your addon

    (xbmc-vimcasts)jon@lenovo ~/Code/xbmc-vimcasts (master) $ xam release

      oooo    ooo  .oooo.   ooo. .oo.  .oo.
       `88b..8P'  `P  )88b  `888P"Y88bP"Y88b
         Y888'     .oP"888   888   888   888
       .o8"'88b   d8(  888   888   888   888
      o88'   888o `Y888""8o o888o o888o o888o

               (XBMC ADDON MANAGER)

      I'm going to help you create a new release for VimCasts.

    .. Init ..

    Please answer the following:
    [?] I see you are using git. Is master the branch you want to use for the release? (Y/n) 
    [?] This release will be for XBMC EDEN. Is this correct? (Y/n) 

    .. Release Metadata for plugin.video.vimcasts ..

    [?] The current version is 1.1. What should the new version be? [1.2] 1.1
    Writing new version to addon.xml...OK
    [?] I see your addon has a few dependencies. Would you like to check for new versions? (Y/n) 
    Starting new HTTP connection (1): mirrors.xbmc.org
    Dependency script.module.xbmcswift2 is already at the newest version.
    [?] I see you have a changelog.txt. Would you like to update it now? (Y/n) n
    [?] I'm ready to commit the changes and tag the release. Should we continue? (Y/n) y

    .. Release 1.1..

    Adding local changes to staging...OK
    [master d5e32ee] [xam-release-script] creating release for version 1.1
     1 file changed, 6 insertions(+), 7 deletions(-)
    Creating commit...OK
    Tagging release...OK
    Counting objects: 5, done.
    Delta compression using up to 2 threads.
    Compressing objects: 100% (3/3), done.
    Writing objects: 100% (3/3), 385 bytes, done.
    Total 3 (delta 2), reused 0 (delta 0)
    To git@github.com:jbeluch/xbmc-vimcasts.git
       63e631c..d5e32ee  HEAD -> master
    Counting objects: 1, done.
    Writing objects: 100% (1/1), 164 bytes, done.
    Total 1 (delta 0), reused 0 (delta 0)
    To git@github.com:jbeluch/xbmc-vimcasts.git
     * [new tag]         1.1 -> 1.1
    Pushing commit and tags to remote...OK

    Congrats. Release was successful.

    +--------------------+
    | Mailing List Email |
    +--------------------+

    To: xbmc-addons@lists.sourceforge.net
    Subject: [git pull] plugin.video.vimcasts

    *addon - plugin.video.vimcasts
    *version - 1.1
    *url - git://github.com/jbeluch/xbmc-vimcasts.git
    *tag - 1.1
    *xbmc version - eden
