# -*- coding: utf-8 -*-
# commfunc.py
from  __future__  import unicode_literals

import sys
import xbmc,xbmcgui,xbmcaddon,xbmcvfs,json,gzip,io,os,csv,time,shutil,collections

try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass
from traceback import format_exc

try:
    import cPickle as pickle
except ImportError:
    import pickle

from datetime import datetime

from urllib import parse
from urllib import request

def get_installedversion():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    #json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = json.loads(json_query)
    version=14
    if 'result' in json_query:
        if 'version' in json_query['result']:
            version=int(json_query['result']['version']['major'])
    return version
version=get_installedversion()
        
def keyboard(title=u'请输入搜索关键字',text=''):
    kb=xbmc.Keyboard(text,title)
    kb.doModal()
    text=''
    if kb.isConfirmed():
        text=kb.getText()
    return text

class MyRedirectHandler(request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        setcookie = str(headers["Set-Cookie"])
        req.add_header("Cookie", setcookie)
        return request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

def _http(url, data=None,referer=None,cookie=None):
    #url=url
    reponse=''
    for i in range(1,5):
        try:
            req = request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)')
            req.add_header('Accept-encoding', 'gzip,deflate')
            req.add_header('Accept-Language', 'zh-cn')
            if cookie:
                req.add_header('Cookie', cookie)
            if referer:
                req.add_header('Referer', referer)
            opener = request.build_opener(MyRedirectHandler)
            if data:
                #data=data
                rsp = opener.open(req, data=data, timeout=15)
            else:
                rsp = opener.open(req, timeout=15)
            
            if rsp.info().get('Content-Encoding') == 'gzip':
                reponse = gzip.GzipFile(fileobj=io.BytesIO(rsp.read())).read()
            else:
                reponse = rsp.read()
            if isinstance(reponse,bytes):
                reponse= reponse.decode('utf-8', 'strict')
            if 'Set-Cookie' in rsp.headers:
                reponse='Set_Cookie:'+rsp.headers['Set-Cookie']+'\r'+reponse
            rsp.close()
            break
        except Exception as e:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            
    
    return reponse

def url_is_alive(url):
    try:
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)')
        req.get_method = lambda : 'HEAD'
        response = request.urlopen(req,timeout=10)
        return True
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return False
        
def strOfSize(size):
    '''
    auth: wangshengke@kedacom.com ；科达柯大侠
    递归实现，精确为最大单位值 + 小数点后三位
    '''
    def strofsize(integer, remainder, level):
        if integer >= 1024:
            remainder = integer % 1024
            integer //= 1024
            level += 1
            return strofsize(integer, remainder, level)
        else:
            return integer, remainder, level

    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    integer, remainder, level = strofsize(size, 0, 0)
    if level+1 > len(units):
        level = -1
    return ( '{}.{:>03d} {}'.format(integer, remainder, units[level]) )

def encode_obj(in_obj):
    def encode_list(in_list):
        out_list = []
        for el in in_list:
            out_list.append(encode_obj(el))
        return out_list

    def encode_dict(in_dict):
        out_dict = {}
        for k, v in in_dict.items():
            out_dict[k] = encode_obj(v)
        return out_dict

    if isinstance(in_obj,str):
        return in_obj.encode('utf-8', 'strict')
    elif isinstance(in_obj, list):
        return encode_list(in_obj)
    elif isinstance(in_obj, tuple):
        return tuple(encode_list(in_obj))
    elif isinstance(in_obj, dict):
        return encode_dict(in_obj)
    return in_obj

def notify(msg='', title=None, delay=5000, image=''):
    '''Displays a temporary notification message to the user. If
    title is not provided, the plugin name will be used. To have a
    blank title, pass '' for the title argument. The delay argument
    is in milliseconds.
    '''
    if not msg:
        xbmc.log(msg='Empty message for notification dialog',level=xbmc.LOGWARNING)
    if title is None:
        title = xbmcaddon.Addon().getAddonInfo('name')
    xbmcgui.Dialog().notification(heading=title, message=msg, time=delay, icon=image)
    
