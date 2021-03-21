# -*- coding: utf-8 -*-
#VERSION: 1.00
from  __future__  import unicode_literals
import json,re
import xbmc,xbmcgui
from commfunc import keyboard,_http,encode_obj,strOfSize, get_storage
from lib.six.moves.urllib import parse
from traceback import format_exc

try:
    import Queue
except ImportError:
    import queue as Queue
import threading

# Called by each thread
def get_url(q, url):
    q.put(_http(url))
    
class bthaha(object):
    url = 'https://wangzhi.men/bthaha'
    name = 'bthaha'
    support_sort = ['relevance','addtime','size']
    page_result_count=10;
    supported_categories = {'all': ''}

    def __init__(self):
        pass
        
    def getsearchurl(self):
        try:
            magneturls=get_storage('magneturls')
            pageresult = _http(self.url)
            match = re.search(r'<strong><a\x20href="(.*?)"', pageresult, re.DOTALL | re.MULTILINE)
            baseurl=''
            if match:
                magneturls[self.name]= match.group(1).rstrip('/')
            else:
                magneturls[self.name]= 'https://glz.bthaha.monster'
            magneturls.sync()
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            
    def search(self, what, cat='all',sorttype='relevance',page='1'):
        result={}
        result['state']=False
        result['list']=[]
        
        
        try:
            # pageresult = _http(self.url)
            # match = re.search(r'<strong><a\x20href="(.*?)"', pageresult, re.DOTALL | re.MULTILINE)
            # baseurl=''
            # if match:
                # baseurl = match.group(1).rstrip('/')
            # if baseurl:
            magneturls=get_storage('magneturls')
            baseurl=magneturls[self.name]
            if sorttype=='addtime': sorttype='create_time'
            elif sorttype=='size': sorttype='length'
            else : sorttype='relavance'
            searchurl='%s/search/%s/?c=&s=%s&p=%s'%(baseurl,parse.quote(what),sorttype,str(int(page)))
            detailurl=[]

            pageresult = _http(searchurl)
            for match in re.finditer(r"title[\x22\x27]\s+href\x3D[\x22\x27]\x2Fwiki\x2F(?P<hashes>.*?)\x2Ehtml[\x22\x27]", pageresult, re.IGNORECASE | re.DOTALL):
                detailurl.append('%s/api/json_info?hashes=%s'%(baseurl,match.group('hashes')))
            q = Queue.Queue()

            for u in detailurl:
                t = threading.Thread(target=get_url, args = (q,u))
                t.daemon = True
                t.start()
            for u in detailurl:
                try:
                    rsp = q.get(block=True, timeout=4)
                    jsonrsp = json.loads(rsp[rsp.index('{'):])
                    #xbmcgui.Dialog().notification(heading='bthaha', message='aaa')
                    for res in jsonrsp['result']:
                        res_dict = dict()
                        res_dict['name'] = res['name']
                        res_dict['size'] = strOfSize(int(res['length']))
                        res_dict['filecount'] = ''
                        res_dict['seeds'] = ''
                        res_dict['leech'] = ''
                        res_dict['link'] = r'magnet:?xt=urn:btih:'+res['info_hash']
                        res_dict['date'] =res['create_time']
                        res_dict['desc_link'] = ''
                        res_dict['engine_url'] = self.url
                        result['list'].append(res_dict)
                except:
                    xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
                    break
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            return result
        
        result['state']=True
        return result