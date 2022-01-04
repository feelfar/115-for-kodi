# -*- coding: utf-8 -*-
#VERSION: 1.00
from  __future__  import unicode_literals
import json,re
import xbmc,xbmcgui
from commfunc import keyboard,_http,encode_obj, get_storage
from lib.six.moves.urllib import parse
from traceback import format_exc

class xccl(object):
    url = 'https://fwonggh.gitlab.io/xccl/'
    name = 'xccl'
    support_sort=['relevance','addtime','size','popular']
    page_result_count=30;
    supported_categories = {'all': ''}

    def __init__(self):
        pass

    def getsearchurl(self):
        try:
            magneturls=get_storage('magneturls')
            pageresult = _http(self.url)
            match = re.search(r'window\x2elocation\x2ehref\x3D[\x22\x27](.*?)[\x22\x27]', pageresult, re.DOTALL | re.MULTILINE)
            if match:
                magneturls[self.name]= match.group(1).rstrip('/')
            else:
                magneturls[self.name]= 'https://xccl.vip'
            magneturls.sync()
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            
    def search(self, what, cat='all',sorttype='relevance',page='1'): 
    
        result={}
        result['state']=False
        result['list']=[]
        result['sorttype']=sorttype
        
        if sorttype=='addtime': sorttype='-time-'
        elif sorttype=='size': sorttype='-length-'
        elif sorttype=='relevance': sorttype='-'
        else : sorttype='-requests-'
        
        try:
            #searchurl='https://btsow.pw'
            # pageresult = _http(self.url)
            # match = re.search(r'<strong><a\x20href="(.*?)"', pageresult, re.DOTALL | re.MULTILINE)
            # if match:
                # searchurl = match.group(1)
            magneturls=get_storage('magneturls')
            searchurl=magneturls[self.name]
            searchurl=searchurl+'/search/kw-%s%s%s.html'%(parse.quote(what),str(sorttype),str(int(page)))

            pageresult = _http(searchurl)
            #xbmc.log(msg=pageresult)
            rmain=r'\x3Ca\s+title\x3D[\x22\x27](?P<title>.*?)[\x22\x27]\s+href\x3D[\x22\x27]\x2Fhash\x2F(?P<magnet>[a-z0-9]{40})\x2Ehtml[\x22\x27].*?文件大小.*?\x3Cb.*?\x3E(?P<filesize>.*?)\x3C\x2Fb\x3E.*?创建时间.*?\x3Cb.*?\x3E(?P<createtime>.*?)\x3C\x2Fb\x3E.*?下载热度.*?\x3Cb.*?\x3E(?P<pop>.*?)\x3C\x2Fb\x3E'
            reobj = re.compile(rmain, re.DOTALL)
            
            for match in reobj.finditer(pageresult):
                title=match.group('title')
                filesize=match.group('filesize')
                createtime=match.group('createtime')
                magnet=r'magnet:?xt=urn:btih:'+match.group('magnet')
                
                res_dict = dict()
                res_dict['name'] = title
                res_dict['size'] = filesize
                res_dict['seeds'] = ''
                res_dict['leech'] = ''
                res_dict['link'] = magnet
                res_dict['date'] =createtime
                res_dict['desc_link'] = ''
                res_dict['engine_url'] = self.url
                result['list'].append(res_dict)
            if len(result['list'])>0:
                result['nextpage']=True
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            return result
        
        result['state']=True
        return result
      