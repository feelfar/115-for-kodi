# -*- coding: utf-8 -*-
#VERSION: 1.00
from  __future__  import unicode_literals
import sys 
sys.path.append("..")
import json,re
import xbmc,xbmcgui
from commfunc import keyboard,_http,encode_obj,url_is_alive

from traceback import format_exc
import comm
from urllib import parse
plugin = comm.plugin

class clzhizhu(object):
    url = 'https://clzhizhu.com/'
    name = 'clzhizhu'
    support_sort=['relevance','addtime','size','popular']
    page_result_count=20;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def getsearchurl(self):
        magneturls=plugin.get_storage('magneturls')
        try:
            rsp= _http('https://clzhizhu.com/')
            #xbmc.log(msg=rsp,level=xbmc.LOGERROR)
            match = re.search(r'clickable-text\x22\x3E(?P<url>.*?)\x3C\x2Fdiv', rsp, re.IGNORECASE | re.DOTALL)
            if match:
                xbmc.log(msg='https://' + [match.group('url').strip().rstrip('/')],level=xbmc.LOGERROR)
                magneturls[self.name] = 'https://' + [match.group('url')[0].strip().rstrip('/')]
            else:
                magneturls[self.name]= 'https://' + 'www.clzz1067.shop'
            magneturls.sync()
        except:
            magneturls[self.name]= 'https://' + 'www.clzz1067.shop'
            magneturls.sync()
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='2'
        elif sorttype=='size': sorttype='1'
        elif sorttype=='popular': sorttype='3'
        else : sorttype='0'
        magneturls=plugin.get_storage('magneturls')
        searchurl=magneturls[self.name]
        searchurl='%s/search-%s-0-%s-%s.html'%(searchurl,parse.quote(what),str(sorttype),str(int(page)))
        try:
            pageresult = _http(searchurl)
            rmain=r'\x2Fhash\x2F(?P<magnet>[a-z0-9]{40})\x2Ehtml.*?[\x22\x27]\x3E(?P<title>.*?)\x3C\x2Fa\x3E.*?添加時間\x3A(?P<createtime>.*?)\x3C\x2Fspan.*?大小\x3A(?P<filesize>.*?)\x3C\x2Fspan'
            reobj = re.compile(rmain, re.IGNORECASE | re.DOTALL)
            for match in reobj.finditer(pageresult):
                
                title = re.sub(r'<[^>]*>','',match.group('title')).strip()
                filesize=re.sub(r'<[^>]*>','',match.group('filesize')).strip()
                createtime=re.sub(r'<[^>]*>','',match.group('createtime')).strip()
                
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
