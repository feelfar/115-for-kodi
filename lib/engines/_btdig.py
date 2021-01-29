# -*- coding: utf-8 -*-
#VERSION: 1.00
from  __future__  import unicode_literals
import json,re
from commfunc import keyboard,_http,encode_obj
from six.moves.urllib import parse
from traceback import format_exc
from xbmcswift2 import Plugin
plugin=Plugin()
class btdig(object):
    url = 'https://btdig.com/search?'
    name = 'btdig'
    support_sort=['relevance','addtime','size','files'];
    page_result_count=10;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='2'
        elif sorttype=='size': sorttype='3'
        elif sorttype=='files': sorttype='4'
        else : sorttype='0'
        
        searchurl=self.url+'q=%s&p=%s&order=%s'%(parse.quote(what),str(int(page)-1),str(sorttype))
        
        try:
            plugin.log.error(searchurl)
            pageresult = _http(searchurl,referer=searchurl)
            plugin.log.error(pageresult)
            rmain=r'torrent_name.*?href.*?\x3E(?P<title>.*?)\x3C\x2Fa\x3E.*?torrent_files.*?\x3E(?P<filecount>.*?)\x3C\x2Fspan\x3E.*?torrent_size.*?\x3e(?P<size>.*?)\x3C\x2Fspan\x3E.*?torrent_age.*?\s*found\s*(?P<date>.*?)\x3C\x2Fspan\x3E.*?torrent_magnet.*?href\x3D\x22(?P<link>.*?)\x22'
            reobj = re.compile(rmain, re.DOTALL)
            for match in reobj.finditer(pageresult):
                title=match.group('title')
                title = re.sub(r'\x3cb.*?\x3e(.*?)\x3c\x2Fb\x3E', r'\1', title, re.IGNORECASE | re.DOTALL)
                title=title.replace('<b>','').replace('</b>','')
                #plugin.notify(title)
                res_dict = dict()
                res_dict['name'] = title
                res_dict['size'] = match.group('size')
                res_dict['filecount'] = match.group('filecount')
                res_dict['seeds'] = ''
                res_dict['leech'] = ''
                res_dict['link'] = match.group('link')
                res_dict['date'] =match.group('date')
                res_dict['desc_link'] = ''
                res_dict['engine_url'] = self.url
                result['list'].append(res_dict)
            if pageresult.find('Next →</a>')>=0:
                result['nextpage']=True
        except:
            plugin.log.error(format_exc())
            return result
        
        result['state']=True
        return result