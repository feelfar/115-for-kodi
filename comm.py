# -*- coding: utf-8 -*-
# comm.py
from  __future__  import unicode_literals

import sys

import xbmc,xbmcvfs,json,gzip,time,os

try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass
from traceback import format_exc

__cwd__ = os.path.dirname(__file__)
__lib__ = xbmc.translatePath( os.path.join( __cwd__, 'lib' ) )
sys.path.append (__lib__)
#sys.path.append (xbmc.translatePath( os.path.join(__lib__,'nova') ))
__resource__ = xbmc.translatePath( os.path.join( __cwd__, 'resources' ))
IMAGES_PATH = xbmc.translatePath(os.path.join(__resource__, 'media'))
__subpath__ = xbmc.translatePath( os.path.join( __cwd__, 'subtitles') )
if not os.path.exists(__subpath__):
    os.makedirs(__subpath__)
__temppath__  = xbmc.translatePath( os.path.join( __cwd__, 'temp') )
if not os.path.exists(__temppath__):
    os.makedirs(__temppath__)

import six
from six.moves.urllib import parse
from six.moves.urllib import request
from six.moves import http_cookiejar as cookielib
from commfunc import get_storage

from xbmcswift2 import Plugin
plugin = Plugin()
setthumbnail=False

moviepoint={}
subcache=get_storage('subcache')
searchvalues=get_storage('searchvalues')

colors = {'dir': 'FF9966','video': 'FF0033','bt': '33FF00', 'audio': '66CCCC', 'subtitle':'505050', 'image': '99CC33',
        'back': '0099CC','next':'CCCCFF', 'menu':'CCFF66', 'star1':'FFFF00','star0':'777777','sort':'666699','filter':'0099CC',
        '-1':'FF0000','0':'8B4513','1':'CCCCFF','2':'7FFF00'}

ALL_VIEW_CODES = {
    'list': {
        'skin.confluence': 50, # List
        'skin.estuary': 55, # List
        'skin.aeon.nox': 50, # List
        'skin.droid': 50, # List
        'skin.quartz': 50, # List
        'skin.re-touched': 50, # List
    },
    'thumbnail': {
        'skin.confluence': 500, # Thumbnail
        'skin.estuary': 500, # Thumbnail
        'skin.estouchy': 500, # Thumbnail
        'skin.aeon.nox': 500, # Wall
        'skin.droid': 51, # Big icons
        'skin.quartz': 51, # Big icons
        'skin.re-touched': 500, #re-touched
        'skin.confluence-vertical': 500,
        'skin.jx720': 52,
        'skin.pm3-hd': 53,
        'skin.rapier': 50,
        'skin.simplicity': 500,
        'skin.slik': 53,
        'skin.touched': 500,
        'skin.transparency': 53,
        'skin.xeebo': 55,
    },
}

def colorize_label(label, _class=None, color=None):
    color = color or colors.get(_class)

    if not color:
        return label

    if len(color) == 6:
        color = 'FF' + color

    return '[COLOR %s]%s[/COLOR]' % (color, label)

@plugin.route('/showpic/<imageurl>')
def showpic(imageurl):
    xbmc.executebuiltin("ShowPicture(%s)" % (imageurl))
    return

@plugin.route('/shellopenurl/<url>/<samsung>')
def shellopenurl(url,samsung):
    osWin = xbmc.getCondVisibility('system.platform.windows')
    osOsx = xbmc.getCondVisibility('system.platform.osx')
    osLinux = xbmc.getCondVisibility('system.platform.linux')
    osAndroid = xbmc.getCondVisibility('System.Platform.Android')
    if osOsx:    
        # ___ Open the url with the default web browser
        xbmc.executebuiltin("System.Exec(open "+url+")")
    elif osWin:
        # ___ Open the url with the default web browser
        xbmc.executebuiltin("System.Exec("+url+")")
    elif osLinux and not osAndroid:
        # ___ Need the xdk-utils package
        xbmc.executebuiltin("System.Exec(xdg-open "+url+")") 
    elif osAndroid:
        androidbrowser='com.android.browser'
        if str(samsung)=='1':
            androidbrowser='com.samsung.vrvideo'
        # ___ Open media with standard android web browser
        xbmc.executebuiltin('StartAndroidActivity(%s,android.intent.action.VIEW,,%s)'%(androidbrowser,url))
        

