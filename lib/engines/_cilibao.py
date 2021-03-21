# -*- coding: utf-8 -*-
#VERSION: 1.00

from  __future__  import unicode_literals
import json,re
from commfunc import keyboard,_http,encode_obj
from lib.six.moves.urllib import parse
from traceback import format_exc

class cilibao(object):
    url = 'https://contact.3400.org/'
    name = 'cilibao'
    support_sort=['relevance','addtime','size','popular']
    page_result_count=10;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        try:
            pageresult = _http(self.url)
            match = re.search(r'href\x3D[\x22\x27](?P<baseurl>.*?)[\x22\x27]\s+target', pageresult, re.DOTALL | re.MULTILINE)
            baseurl=''
            if match:
                baseurl = match.group('baseurl').rstrip('/')
            if baseurl:
                if sorttype=='addtime': sorttype='time'
                elif sorttype=='size': sorttype='size'
                elif sorttype=='relevance': sorttype='rel'
                else : sorttype='hits'
                
                searchurl='%s/s/%s_%s_%s.html'%(baseurl,parse.quote(what),str(sorttype),str(int(page)))
                pageresult = _http(searchurl)
                #plugin.log.error(pageresult)
                rmain=r'\x2Fbt\x2F(?P<magnet>[a-z0-9]{40})\x2Ehtml.*?blank[\x22\x27]\x3E(?P<title>.*?)\x3C\x2Fa\x3E.*?创建时间.*?\x3Cb\x3E(?P<createtime>.*?)\x3C\x2Fb\x3E.*?文件大小.*?\x3E(?P<filesize>.*?)\x3C\x2Fb\x3E'
                reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
                for match in reobj.finditer(pageresult):
                    
                    title=match.group('title').replace('<em>','').replace('</em>','')
                    filesize=match.group('filesize')
                    createtime=match.group('createtime')
                    
                    magnet=r'magnet:?xt=urn:btih:'+match.group('magnet')
                    
                    res_dict = dict()
                    res_dict['name'] = title
                    res_dict['size'] = filesize
                    res_dict['filecount'] = ''
                    res_dict['seeds'] = ''
                    res_dict['leech'] = ''
                    res_dict['link'] = magnet
                    res_dict['date'] =createtime
                    res_dict['desc_link'] = ''
                    res_dict['engine_url'] = self.url
                    result['list'].append(res_dict)
                if pageresult.find('&raquo;')>=0:
                    result['nextpage']=True
        except Exception as ex:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            return result
        
        result['state']=True
        return result
