# -*- coding: utf-8 -*-
# magnet.py
#siteurl#btdig#https://btdigg.unblockit.dev# #siteurl#
from  __future__  import unicode_literals
import xbmc,xbmcgui,xbmcvfs,os,sys
try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass
import comm,six
plugin = comm.plugin
IMAGES_PATH = comm.IMAGES_PATH
from commfunc import keyboard,_http,encode_obj,notify,ListItem

import nova2

@plugin.route('/btsearchInit/<sstr>/<modify>')
def btsearchInit(sstr='',modify='0'):
    if sstr=='0':sstr=''
    if not sstr or sstr=='0' or modify=='1':
        sstr = keyboard(text=sstr)
        if not sstr:
            return

    
    items=[]
    items.append({'label': '编辑搜索关键字[COLOR FF00FFFF]%s[/COLOR]'%(six.ensure_text(sstr)),
                'path': plugin.url_for(btsearchInit, sstr=six.ensure_binary(sstr), modify='1')})
    items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('相关度',six.ensure_text(sstr)), 
                'path': plugin.url_for(btsearch,enginestr='all',sstr=six.ensure_binary(sstr),sorttype='relevance')})
    items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('创建时间',six.ensure_text(sstr)), 
                'path': plugin.url_for(btsearch,enginestr='all',sstr=six.ensure_binary(sstr),sorttype='addtime')})
    items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('文件大小',six.ensure_text(sstr)), 
                'path': plugin.url_for(btsearch,enginestr='all',sstr=six.ensure_binary(sstr),sorttype='size')})
    items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('文件数量',six.ensure_text(sstr)), 
                'path': plugin.url_for(btsearch,enginestr='all',sstr=six.ensure_binary(sstr),sorttype='files')})
    items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('热度',six.ensure_text(sstr)), 
                'path': plugin.url_for(btsearch,enginestr='all',sstr=six.ensure_binary(sstr),sorttype='popular')})
    btenginelist=nova2.initialize_engines()
    
    
    for btengine in btenginelist:
        items.append({'label': '在[COLOR FFFFFF00]%s[/COLOR]搜索[COLOR FF00FFFF]%s[/COLOR]'%(btengine,six.ensure_text(sstr)),
                'path': plugin.url_for(btsearch,enginestr=btengine,sstr=six.ensure_binary(sstr),sorttype='-1'),
                'thumbnail':xbmc.translatePath(os.path.join( IMAGES_PATH, 'magnet.png')) })
    return items

def anySizeToBytes(size_string):
    """
    Convert a string like '1 KB' to '1024' (bytes)
    """
    # separate integer from unit
    try:
        size, unit = size_string.split()
    except:
        try:
            size = size_string.strip()
            unit = ''.join([c for c in size if c.isalpha()])
            if len(unit) > 0:
                size = size[:-len(unit)]
        except:
            return -1
    if len(size) == 0:
        return -1
    size = float(size)
    if len(unit) == 0:
        return int(size)
    short_unit = unit.upper()[0]

    # convert
    units_dict = {'T': 40, 'G': 30, 'M': 20, 'K': 10}
    if short_unit in units_dict:
        size = size * 2**units_dict[short_unit]
    return int(size)
    
@plugin.route('/btsearch/<enginestr>/<sstr>/<sorttype>')
def btsearch(enginestr,sstr,sorttype):
    if not sstr or sstr=='0':
        return
    max=int(get_setting('btmaxresult'))
    max=(max+1)*20
    items=[]
    if enginestr!='all' and sorttype=='-1':
        engineinfo=nova2.getengineinfo(enginestr)
        supportsort=engineinfo['support_sort']
        if len(supportsort)>0:
            sortkeys={'relevance':'相关度','addtime':'创建时间','size':'文件大小','files':'文件数量','popular':'热度',}
            dialog = xbmcgui.Dialog()
            sortselectlist=[]
            for s in supportsort:
                sortselectlist.append(sortkeys[s])
            sorttype=dialog.select(engineinfo['name']+'选择排序类型',sortselectlist)
            if sorttype==-1:
                return None
            sorttype=supportsort[int(sorttype)]
            #notify(sorttype)
    result=nova2.search(enginestr,sstr,sorttype,maxresult=max)
    msg='共找到%d条磁力链' % (len(result))
    notify(msg)

    for res_dict in result:
        title='[COLOR FF00FFFF]'+res_dict['size']+'[/COLOR]'+'[COLOR FFCCFFCC]'+res_dict['date'][:10]+'[/COLOR]'+res_dict['name']
        filemsg ='大小：'+res_dict['size']+'  创建时间：'+res_dict['date']
        listitem=ListItem(label=comm.colorize_label(title, 'bt'), 
            label2=res_dict['size'], icon=None, thumbnail=None, 
            path=plugin.url_for(execmagnet,url=res_dict['link'],
            title=six.ensure_binary(title),msg=six.ensure_binary(filemsg)))
        #listitem.set_info('picture', {'size': anySizeToBytes(res_dict['size'])})
        context_menu_items=[] 
        if(list=='other'):
            titletype=title
        items.append(listitem)
    return items
