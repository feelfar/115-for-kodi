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

class sokankan(object):
    name = 'sokankan'
    support_sort=['relevance','addtime','size','popular']
    page_result_count=20;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def getsearchurl(self):
        magneturls=plugin.get_storage('magneturls')
        magneturls[self.name] = ''
        magneturls.sync()
        try:
            rsp = _http('https://www.sokankan.top/')
            match = re.search(r'var\s+adurl[0-9]*\s?\x3D\s?[\x22\x27](?P<url>.*?)[\x22\x27]', rsp,  re.IGNORECASE | re.DOTALL)
            if match:
                magneturls[self.name] ='https://'+match.group('url')
                magneturls.sync()
                return
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        
        
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        magneturls=plugin.get_storage('magneturls')
        url=magneturls[self.name]
        if not url:
            return
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='-create'
        elif sorttype=='size': sorttype='-size'
        elif sorttype=='popular': sorttype='-hot'
        else : sorttype=''
        
        if url[-1:]=='/':
            url=url[0:-1]
       
        searchurl='%s/search%s/%s/page-%s.html'%(url,str(sorttype),parse.quote(what),str(int(page)))
        try:
            #xbmc.log(msg=searchurl,level=xbmc.LOGERROR)
            pageresult = _http(searchurl)
            rmain=r'\x2Fhash\x2f(?P<magnet>[a-z0-9]{40}).*?\x2fspan\x3E\x26nbsp\x3b(?P<title>.*?)\x3C\x2f.*?热度：(?P<seeds>.*?)\x26nbsp\x3b.*?文件大小：(?P<filesize>.*?)\x26nbsp\x3b.*?创建时间：(?P<createtime>.*?)\s.*?\x26nbsp\x3b'
            
            for match in re.finditer(rmain, pageresult, re.IGNORECASE | re.DOTALL):
                magnet='magnet:?xt=urn:btih:'+match.group('magnet')
                title=match.group('title')
                filesize=match.group('filesize').strip()
                createtime=match.group('createtime').strip()

                res_dict = dict()
                res_dict['name'] = title
                res_dict['size'] = filesize
                res_dict['filecount'] = ''
                res_dict['seeds'] = ''
                res_dict['leech'] = ''
                res_dict['link'] = magnet
                res_dict['date'] = createtime
                res_dict['desc_link'] = ''
                res_dict['engine_url'] = ''
                result['list'].append(res_dict)
            if pageresult.find('&raquo;')>=0:
                result['nextpage']=True
        except Exception as ex:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            return result
        
        result['state']=True
        #xbmc.log(msg=str(len( result['list'])),level=xbmc.LOGERROR)
        return result
