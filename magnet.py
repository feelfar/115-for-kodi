# -*- coding: utf-8 -*-
# magnet.py

import xbmc,xbmcgui,os,sys
import comm
from xbmcswift2 import ListItem
plugin = comm.plugin
__cwd__=comm.__cwd__
keyboard=comm.keyboard
_http=comm._http

import nova2

@plugin.route('/btsearchInit/<sstr>/<modify>')
def btsearchInit(sstr='',modify='0'):
	if sstr=='0':sstr=''
	if not sstr or sstr=='0' or modify=='1':
		sstr = keyboard(text=sstr)
		if not sstr:
			return

	
	items=[]
	items.append({'label': '编辑搜索关键字[COLOR FF00FFFF]%s[/COLOR]'%(sstr.encode('utf-8')),
				'path': plugin.url_for('btsearchInit', sstr=sstr.encode('utf-8'), modify='1'),
				'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'magnet.jpg') ).decode('utf-8')})
	items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('相关度',sstr.encode('utf-8')), 
				'path': plugin.url_for('btsearch',enginestr='all',sstr=sstr,sorttype='relevance')})
	items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('创建时间',sstr.encode('utf-8')), 
				'path': plugin.url_for('btsearch',enginestr='all',sstr=sstr,sorttype='addtime')})
	items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('文件大小',sstr.encode('utf-8')), 
				'path': plugin.url_for('btsearch',enginestr='all',sstr=sstr,sorttype='size')})
	items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('文件数量',sstr.encode('utf-8')), 
				'path': plugin.url_for('btsearch',enginestr='all',sstr=sstr,sorttype='files')})
	items.append({'label': '按[COLOR FFFF00FF]%s[/COLOR]全搜索[COLOR FF00FFFF]%s[/COLOR]'%('热度',sstr.encode('utf-8')), 
				'path': plugin.url_for('btsearch',enginestr='all',sstr=sstr,sorttype='popular')})
	btenginelist=nova2.initialize_engines()
	
	
	for btengine in btenginelist:
		items.append({'label': '在[COLOR FFFFFF00]%s[/COLOR]搜索[COLOR FF00FFFF]%s[/COLOR]'%(btengine,sstr),
				'path': plugin.url_for('btsearch',enginestr=btengine,sstr=sstr,sorttype='-1')})
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
    if units_dict.has_key(short_unit):
        size = size * 2**units_dict[short_unit]
    return int(size)
	
@plugin.route('/btsearch/<enginestr>/<sstr>/<sorttype>')
def btsearch(enginestr,sstr,sorttype):
	if not sstr or sstr=='0':
		return
	max=int(plugin.get_setting('btmaxresult'))
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
			#plugin.notify(sorttype)
	result=nova2.search(enginestr,sstr,sorttype,maxresult=max)
	msg='共找到%d条磁力链' % (len(result))
	plugin.notify(msg)

	for res_dict in result:
		title='[COLOR FF00FFFF]'+res_dict['size']+'[/COLOR]'+'[COLOR FFCCFFCC]'+res_dict['date'][:10]+'[/COLOR]'+res_dict['name'].encode('UTF-8')
		filemsg ='大小：'+res_dict['size'].encode('UTF-8')+'  创建时间：'+res_dict['date'].encode('UTF-8')
		listitem=ListItem(label=comm.colorize_label(title, 'bt'), 
			label2=res_dict['size'], icon=None, thumbnail=None, 
			path=plugin.url_for('execmagnet',url=res_dict['link'].encode('UTF-8'),
			title=title,msg=filemsg))
		#listitem.set_info('picture', {'size': anySizeToBytes(res_dict['size'])})
		context_menu_items=[] 
		if(list=='other'):
			titletype=title
		items.append(listitem)
	return items
