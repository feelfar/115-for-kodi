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
import lib.six as six
from lib.six.moves import html_parser
from lib.six.moves.urllib import parse
plugin = comm.plugin

class yuhuage(object):
    
    name = 'yuhuage'
    support_sort=['relevance','addtime','size','files','popular']
    page_result_count=20;
    supported_categories = {'all': ''}
    
    def __init__(self):
        pass
        
    def getsearchurl(self):
        magneturls=plugin.get_storage('magneturls')
        magneturls[self.name] = ''
        magneturls.sync()
        try:
            rsp = _http(' https://github.com/yuhuage/dizhi/ ')
            match = re.search(r'备用网址(?:\x3A|：)?\s?\x3ca\s+href\x3D[\x22\x27](?P<url>http.*?)[\x22\x27]\s+', rsp,  re.IGNORECASE | re.DOTALL)
            if match:
                magneturls[self.name] = match.group('url')
                magneturls.sync()
                return
            '''
            match = re.search(r'最新网址(?:\x3A|：)?\s?\x3ca\s+href\x3D[\x22\x27](?P<url>http.*?)[\x22\x27]\s+', rsp,  re.IGNORECASE | re.DOTALL)
            if match:
                xbmc.log(msg=match.group('url'),level=xbmc.LOGERROR)
                if url_is_alive(match.group('url')):
                    xbmc.log(msg=match.group('url'),level=xbmc.LOGERROR)
                    magneturls[self.name] = match.group('url')
                    magneturls.sync()
                    return
            match = re.search(r'备用网址(?:\x3A|：)?\s?\x3ca\s+href\x3D[\x22\x27](?P<url>http.*?)[\x22\x27]\s+', rsp,  re.IGNORECASE | re.DOTALL)
            if match:
                xbmc.log(msg=match.group('url'),level=xbmc.LOGERROR)
                if url_is_alive(match.group('url')):
                    xbmc.log(msg=match.group('url'),level=xbmc.LOGERROR)
                    magneturls[self.name] = match.group('url')
                    magneturls.sync()
                    return
                    '''
                    
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
        
        if sorttype=='addtime': sorttype='time'
        elif sorttype=='size': sorttype='size'
        elif sorttype=='files': sorttype='filenums'
        elif sorttype=='popular': sorttype='views'
        else : sorttype='def'
        
        if url[-1:]=='/':
            url=url[0:-1]
        
        searchurl='%s/search/%s-%s-%s.html'%(url,parse.quote(what),str(int(page)),str(sorttype))
        try:
            xbmc.log(msg=searchurl,level=xbmc.LOGERROR)
            pageresult = _http(searchurl)
            rmain=r'item-title.*?\x3ca\s+href\x3D[\x22\x27](?P<url>.*?)[\x22\x27].*?_blank[\x22\x27]\x3e(?P<title>.*?)\x3c\x2Fa\x3e\x3c\x2Fh3\x3e.*?创建时间.*?\x3cb\x3e(?P<createtime>.*?)\x3c\x2fb\x3e.*?文件大小.*?\x3cb.*?\x3e(?P<filesize>.*?)\x3c\x2fb\x3e.*?文件数量.*?\x3cb.*?\x3e(?P<filecount>.*?)\x3c\x2fb\x3e.*?下载热度.*?\x3cb.*?\x3e(?P<seeds>.*?)\x3c\x2fb\x3e'
            
            for match in re.finditer(rmain, pageresult, re.IGNORECASE | re.DOTALL):
                xbmc.log(msg=match.group('url'),level=xbmc.LOGERROR)
                detalresult=_http(url+match.group('url'))
                match2 = re.search("href\x3D[\x22\x27](?P<magnet>magnet.*?)[\x22\x27]", detalresult, re.IGNORECASE | re.DOTALL)
                if match2:
                    magnet = match2.group("magnet")
                else:
                    magnet = ""
                    
                title=match.group('title').replace('<b>','').replace('</b>','')
                title = re.sub("\x3cspan.*?\x3c\x2Fspan\x3e", "", title, 0, re.IGNORECASE | re.DOTALL).strip()
                filesize=match.group('filesize').strip()
                createtime=match.group('createtime').strip()
                filecount=match.group('filecount').strip()

                res_dict = dict()
                '''
                res_dict['name'] = title
                res_dict['size'] = filesize
                res_dict['filecount'] = filecount
                res_dict['seeds'] = ''
                res_dict['leech'] = ''
                res_dict['link'] = magnet
                res_dict['date'] =createtime
                res_dict['desc_link'] = ''
                res_dict['engine_url'] = url
                '''
                res_dict['name'] = title
                res_dict['size'] = filesize
                res_dict['filecount'] = filecount
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
        return result
