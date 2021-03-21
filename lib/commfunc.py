# -*- coding: utf-8 -*-
# commfunc.py
from  __future__  import unicode_literals

import sys

import xbmc,xbmcgui,xbmcaddon,xbmcvfs,json,gzip,os,csv,time,shutil,collections

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

import lib.six as six
from lib.six.moves.urllib import parse
from lib.six.moves.urllib import request

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
    buildinkb=False
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
                reponse = gzip.GzipFile(fileobj=six.BytesIO(rsp.read())).read()
            else:
                reponse = rsp.read()
            reponse=six.ensure_text(reponse)
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
        response = request.urlopen(req)
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

    if isinstance(in_obj, six.text_type):
        return six.ensure_binary(in_obj)
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
    

class _PersistentDictMixin(object):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.
    '''

    def __init__(self, filename, flag='c', mode=None, file_format='pickle'):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.file_format = file_format      # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            xbmc.log('Reading %s storage from disk'%(filename),
                      level=xbmc.LOGDEBUG)
            fileobj = open(filename, 'rb' if file_format == 'pickle' else 'r')
            with fileobj:
                self.load(fileobj)

    def sync(self):
        '''Write the dict to disk'''
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.file_format == 'pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()

        # shutil error (SameFileError when performing copyfile)
        if os.path.exists(self.filename):
            os.remove(self.filename)

        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        '''Calls sync'''
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        '''Handles the writing of the dict to the file object'''
        if self.file_format == 'csv':
            csv.writer(fileobj).writerows(self.raw_dict().items())
        elif self.file_format == 'json':
            json.dump(self.raw_dict(), fileobj, separators=(',', ':'))
        elif self.file_format == 'pickle':
            pickle.dump(dict(self.raw_dict()), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' +
                                      repr(self.file_format))

    def load(self, fileobj):
        '''Load the dict from the file object'''
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.initial_update(loader(fileobj))
            except Exception as e:
                pass
        raise ValueError('File not in a supported format')

    def raw_dict(self):
        '''Returns the underlying dict'''
        raise NotImplementedError


class _Storage(collections.MutableMapping, _PersistentDictMixin):
    '''Storage that acts like a dict but also can persist to disk.

    :param filename: An absolute filepath to reprsent the storage on disk. The
                     storage will loaded from this file if it already exists,
                     otherwise the file will be created.
    :param file_format: 'pickle', 'json' or 'csv'. pickle is the default. Be
                        aware that json and csv have limited support for python
                        objets.

    .. warning:: Currently there are no limitations on the size of the storage.
                 Please be sure to call :meth:`~xbmcswift2._Storage.clear`
                 periodically.
    '''

    def __init__(self, filename, file_format='pickle'):
        '''Acceptable formats are 'csv', 'json' and 'pickle'.'''
        self._items = {}
        _PersistentDictMixin.__init__(self, filename, file_format=file_format)

    def __setitem__(self, key, val):
        self._items.__setitem__(key, val)

    def __getitem__(self, key):
        return self._items.__getitem__(key)

    def __delitem__(self, key):
        self._items.__delitem__(key)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def raw_dict(self):
        '''Returns the wrapped dict'''
        return self._items

    initial_update = collections.MutableMapping.update

    def clear(self):
        super(_Storage, self).clear()
        self.sync()

class TimedStorage(_Storage):
    '''A dict with the ability to persist to disk and TTL for items.'''

    def __init__(self, filename, file_format='pickle', TTL=None):
        '''TTL if provided should be a datetime.timedelta. Any entries
        older than the provided TTL will be removed upon load and upon item
        access.
        '''
        self.TTL = TTL
        _Storage.__init__(self, filename, file_format=file_format)

    def __setitem__(self, key, val, raw=False):
        if raw:
            self._items[key] = val
        else:
            self._items[key] = (val, time.time())

    def __getitem__(self, key):
        val, timestamp = self._items[key]
        if self.TTL and (datetime.utcnow() -
            datetime.utcfromtimestamp(timestamp) > self.TTL):
            del self._items[key]
            return self._items[key][0]  # Will raise KeyError
        return val

    def initial_update(self, mapping):
        '''Initially fills the underlying dictionary with keys, values and
        timestamps.
        '''
        for key, val in mapping.items():
            _, timestamp = val
            if not self.TTL or (datetime.utcnow() -
                datetime.utcfromtimestamp(timestamp) < self.TTL):
                self.__setitem__(key, val, raw=True)

def get_storage(name='main', file_format='pickle', TTL=None):
    '''Returns a storage for the given name. The returned storage is a
    fully functioning python dictionary and is designed to be used that
    way. It is usually not necessary for the caller to load or save the
    storage manually. If the storage does not already exist, it will be
    created.

    .. seealso:: :class:`xbmcswift2.TimedStorage` for more details.

    :param name: The name  of the storage to retrieve.
    :param file_format: Choices are 'pickle', 'csv', and 'json'. Pickle is
                        recommended as it supports python objects.

                        .. note:: If a storage already exists for the given
                                  name, the file_format parameter is
                                  ignored. The format will be determined by
                                  the existing storage file.
    :param TTL: The time to live for storage items specified in minutes or None
                for no expiration. Since storage items aren't expired until a
                storage is loaded form disk, it is possible to call
                get_storage() with a different TTL than when the storage was
                created. The currently specified TTL is always honored.
    '''
    addon_id=xbmcaddon.Addon().getAddonInfo('id')
    storage_path = xbmc.translatePath(
        'special://profile/addon_data/%s/.storage/' % addon_id)
    if not os.path.isdir(storage_path):
        os.makedirs(storage_path)
    filename = os.path.join(storage_path, name)
    if TTL:
        TTL = timedelta(minutes=TTL)
    try:
        storage = TimedStorage(filename, file_format, TTL)
    except ValueError:
        # Thrown when the storage file is corrupted and can't be read.
        # Prompt user to delete storage.
        choices = ['Clear storage', 'Cancel']
        ret = xbmcgui.Dialog().select('A storage file is corrupted. It'
                                      ' is recommended to clear it.',
                                      choices)
        if ret == 0:
            os.remove(filename)
            storage = TimedStorage(filename, file_format, TTL)
        else:
            raise Exception('Corrupted storage file at %s' % filename)

    xbmc.log(msg = 'Loaded storage "%s" from disk'%name,level=xbmc.LOGDEBUG)
    return storage