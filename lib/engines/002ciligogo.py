# -*- coding: utf-8 -*-
#VERSION: 1.00

from  __future__  import unicode_literals
import json,re
import xbmc,xbmcgui
from commfunc import keyboard,_http,encode_obj, get_storage,url_is_alive
from lib.six.moves.urllib import parse
from traceback import format_exc

class ciligogo(object):
    url = 'http://www.btmovi.work'
    name = 'ciligogo'
    support_sort=['relevance','addtime','size','popular']
    page_result_count=10;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def getsearchurl(self):
        try:
            magneturls=get_storage('magneturls')
            jubturl='https://jubt.gq/'
            rsp = _http('https://jubt.gitlab.io/home/')
            for match in re.finditer(r"\x3Ctd\x3E\s*\x3Ca\s+href\x3D[\x22\x27](?P<url>.*?)[\x22\x27]", rsp, re.IGNORECASE | re.DOTALL):
                if url_is_alive(match.group('url')):
                    jubturl=match.group('url')
                    break
            rsp= _http(jubturl)
            match = re.search(r"window\x2Eopen\x28[\x22\x27](?P<url>(?:http|https)\x3A[\w\x2E\x2F]*?)[\x22\x27](?:(?!window).)*?strong\x3E磁力蜘蛛\s*\x7C.*?\x3C\x2Fdiv\x3E", rsp, re.IGNORECASE | re.DOTALL)
            if match:
                magneturls[self.name] = [match.group('url').strip().rstrip('/')]
            else:
                magneturls[self.name]= 'http://www.btmovi.work'
            magneturls.sync()
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='time'
        elif sorttype=='size': sorttype='size'
        elif sorttype=='relevance': sorttype='rel'
        else : sorttype='hits'
        magneturls=get_storage('magneturls')
        searchurl=magneturls[self.name]
        searchurl='%s/so/%s_%s_%s.html'%(searchurl,parse.quote(what),str(sorttype),str(int(page)))
        try:
            pageresult = _http(searchurl)
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
