# -*- coding: utf-8 -*-
# commfunc.py
from  __future__  import unicode_literals

import sys

import xbmc,xbmcgui,xbmcaddon,xbmcvfs,xbmcplugin,json,gzip,os,csv,time,shutil,collections

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

import six
from six.moves.urllib import parse
from six.moves.urllib import request

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
    req = request.Request(url)
    req.get_method = lambda : 'HEAD'
    try:
        response = request.urlopen(req)
        return True
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return False
        
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
    

def get_setting(key, converter=None, choices=None):
    '''Returns the settings value for the provided key.
    If converter is str, unicode, bool or int the settings value will be
    returned converted to the provided type.
    If choices is an instance of list or tuple its item at position of the
    settings value be returned.
    .. note:: It is suggested to always use unicode for text-settings
              because else xbmc returns utf-8 encoded strings.

    :param key: The id of the setting defined in settings.xml.
    :param converter: (Optional) Choices are str, unicode, bool and int.
    :param converter: (Optional) Choices are instances of list or tuple.

    Examples:
        * ``get_setting('per_page', int)``
        * ``get_setting('password', unicode)``
        * ``get_setting('force_viewmode', bool)``
        * ``get_setting('content', choices=('videos', 'movies'))``
    '''
    #TODO: allow pickling of settings items?
    # TODO: STUB THIS OUT ON CLI
    value = xbmcaddon.Addon().getSetting(id=key)

    if converter is str:
        return value
    elif converter is bool:
        return value == 'true'
    elif converter is int:
        return int(value)
    elif isinstance(choices, (list, tuple)):
        return choices[int(value)]
    elif converter is None:
        return value
    else:
        raise TypeError('Acceptable converters are str, unicode, bool and '
                        'int. Acceptable choices are instances of list '
                        ' or tuple.')

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


class ListItem(object):
    '''A wrapper for the xbmcgui.ListItem class. The class keeps track
    of any set properties that xbmcgui doesn't expose getters for.
    '''
    def __init__(self, label=None, label2=None, icon=None, thumbnail=None,
                 path=None, fanart=None):
        '''Defaults are an emtpy string since xbmcgui.ListItem will not
        accept None.
        '''
        kwargs = {
            'label': label,
            'label2': label2,
            'path': path
        }
        #kwargs = dict((key, val) for key, val in locals().items() if val is
        #not None and key != 'self')
        kwargs = dict((key, val) for key, val in kwargs.items()
                      if val is not None)
        self._listitem = xbmcgui.ListItem(**kwargs)

        # kodi doesn't make getters available for these properties so we'll
        # keep track on our own
        self._path = path
        self._context_menu_items = []
        self.is_folder = True
        self._played = False
        self._art = {'icon': icon, 'thumb': thumbnail, 'fanart': fanart}

        # set listitem art
        self._listitem.setArt(self._art)

    def __repr__(self):
        return ("<ListItem '%s'>" % self.label).encode('utf-8')

    def __str__(self):
        return ('%s (%s)' % (self.label, self.path)).encode('utf-8')

    def get_context_menu_items(self):
        '''Returns the list of currently set context_menu items.'''
        return self._context_menu_items

    def add_context_menu_items(self, items):
        '''Adds context menu items. replace_items is only kept for
        legacy reasons, its functionality was removed.
        '''
        for label, action in items:
            assert isinstance(label, basestring)
            assert isinstance(action, basestring)

        self._context_menu_items.extend(items)
        self._listitem.addContextMenuItems(items)

    def get_label(self):
        '''Sets the listitem's label'''
        return self._listitem.getLabel()

    def set_label(self, label):
        '''Returns the listitem's label'''
        return self._listitem.setLabel(label)

    label = property(get_label, set_label)

    def get_label2(self):
        '''Returns the listitem's label2'''
        return self._listitem.getLabel2()

    def set_label2(self, label):
        '''Sets the listitem's label2'''
        return self._listitem.setLabel2(label)

    label2 = property(get_label2, set_label2)

    def is_selected(self):
        '''Returns True if the listitem is selected.'''
        return self._listitem.isSelected()

    def select(self, selected_status=True):
        '''Sets the listitems selected status to the provided value.
        Defaults to True.
        '''
        return self._listitem.select(selected_status)

    selected = property(is_selected, select)

    def set_info(self, type, info_labels):
        '''Sets the listitems info'''
        return self._listitem.setInfo(type, info_labels)

    def get_property(self, key):
        '''Returns the property associated with the given key'''
        return self._listitem.getProperty(key)

    def set_property(self, key, value):
        '''Sets a property for the given key and value'''
        return self._listitem.setProperty(key, value)

    def add_stream_info(self, stream_type, stream_values):
        '''Adds stream details'''
        return self._listitem.addStreamInfo(stream_type, stream_values)

    def get_icon(self):
        '''Returns the listitem's icon image'''
        return self._art['icon']

    def set_icon(self, icon):
        '''Sets the listitem's icon image'''
        self._art['icon'] = icon
        return self._listitem.setArt(self._art)

    icon = property(get_icon, set_icon)

    def get_thumbnail(self):
        '''Returns the listitem's thumbnail image'''
        return self._art['thumbnail']

    def set_thumbnail(self, thumbnail):
        '''Sets the listitem's thumbnail image'''
        self._art['thumbnail'] = thumbnail
        return self._listitem.setArt(self._art)

    def set_art(self, art):
        self._art = art
        return self._listitem.setArt(self._art)

    thumbnail = property(get_thumbnail, set_thumbnail)

    def get_path(self):
        '''Returns the listitem's path'''
        return self._path

    def set_path(self, path):
        '''Sets the listitem's path'''
        self._path = path
        return self._listitem.setPath(path)

    path = property(get_path, set_path)

    def get_is_playable(self):
        '''Returns True if the listitem is playable, False if it is a
        directory
        '''
        return not self.is_folder

    def set_is_playable(self, is_playable):
        '''Sets the listitem's playable flag'''
        value = 'false'
        if is_playable:
            value = 'true'
        self.set_property('isPlayable', value)
        self.is_folder = not is_playable

    playable = property(get_is_playable, set_is_playable)

    def set_played(self, was_played):
        '''Sets the played status of the listitem. Used to
        differentiate between a resolved video versus a playable item.
        Has no effect on KODI, it is strictly used for xbmcswift2.
        '''
        self._played = was_played

    def get_played(self):
        '''Returns True if the video was played.'''
        return self._played

    def as_tuple(self):
        '''Returns a tuple of list item properties:
            (path, the wrapped xbmcgui.ListItem, is_folder)
        '''
        return self.path, self._listitem, self.is_folder

    def as_xbmc_listitem(self):
        '''Returns the wrapped xbmcgui.ListItem'''
        return self._listitem

    @classmethod
    def from_dict(cls, label=None, label2=None, icon=None, thumbnail=None,
                  path=None, selected=None, info=None, properties=None,
                  context_menu=None, replace_context_menu=False,
                  is_playable=None, info_type='video', stream_info=None, fanart=None):
        '''A ListItem constructor for setting a lot of properties not
        available in the regular __init__ method. Useful to collect all
        the properties in a dict and then use the **dct to call this
        method.
        '''
        icon=thumbnail
        listitem = cls(label, label2, icon, thumbnail, path, fanart)

        if selected is not None:
            listitem.select(selected)

        if info:
            listitem.set_info(info_type, info)

        if is_playable:
            listitem.set_is_playable(True)

        if properties:
            # Need to support existing tuples, but prefer to have a dict for
            # properties.
            if hasattr(properties, 'items'):
                properties = properties.items()
            for key, val in properties:
                listitem.set_property(key, val)

        if stream_info:
            for stream_type, stream_values in stream_info.items():
                listitem.add_stream_info(stream_type, stream_values)

        if context_menu:
            listitem.add_context_menu_items(context_menu)

        return listitem

        
def _listitemify(item):
    '''Creates an xbmcswift2.ListItem if the provided value for item is a
    dict. If item is already a valid xbmcswift2.ListItem, the item is
    returned unmodified.
    '''
    # Create ListItems for anything that is not already an instance of
    # ListItem
    if not hasattr(item, 'as_tuple'):
        item = ListItem.from_dict(**item)
    return item

def add_items(handle, items):
    '''Adds ListItems to the KODI interface. Each item in the
    provided list should either be instances of xbmcswift2.ListItem,
    or regular dictionaries that will be passed to
    xbmcswift2.ListItem.from_dict. Returns the list of ListItems.

    :param items: An iterable of items where each item is either a
                  dictionary with keys/values suitable for passing to
                  :meth:`xbmcswift2.ListItem.from_dict` or an instance of
                  :class:`xbmcswift2.ListItem`.
    '''
    _items = [_listitemify(item) for item in items]
    tuples = [item.as_tuple() for item in _items]
    xbmcplugin.addDirectoryItems(handle, tuples, len(tuples))
    xbmcplugin.endOfDirectory(handle)
