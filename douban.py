# -*- coding: utf-8 -*-
# douban.py

import xbmc,xbmcgui,os,sys,re,time,urllib,json
import comm
plugin = comm.plugin
setthumbnail=comm.setthumbnail
__cwd__=comm.__cwd__
keyboard=comm.keyboard
_http=comm._http
colorize_label=comm.colorize_label
from xbmcswift2 import ListItem

clipandphotos=plugin.get_storage('clipandphotos')

@plugin.route('/dbplaytrailer/<movid>')
def dbplaytrailer(movid):
	videourl=''
	try:
		url='https://movie.douban.com/trailer/'+movid+'/#content'
		#xbmc.log(url)
		rsp= _http(url)
		match = re.search(r'video\s+id.*?source\s+src\x3D[\x27\x22](?P<videourl>.*?)[\x27\x22]', rsp, re.DOTALL | re.MULTILINE)
		if match:
			videourl = match.group('videourl')
		if videourl!='':
			plugin.set_resolved_url(videourl)
	except:
		return
	

@plugin.route('/dbtrailer')
def dbtrailer():
	menus=[]
	for clip in clipandphotos['clips']:
		menus.append({'label':clip['title'],
			'path': clip['resource_url'],
			'thumbnail': clip['medium'],
			'is_playable':True, 
			'info_type':'video',
			'info':{'title':clip['title']}
			})
	i=1
	for photo in clipandphotos['photos']:
		menus.append({'label':'Photo:%d'%(i),
			'path': plugin.url_for('showpic', imageurl=photo['image']),
			'thumbnail': photo['thumb'],
			
			})
		i+=1
	setthumbnail['set']=True
	return menus

@plugin.route('/dbsummary/<summary>')
def dbsummary(summary):
	dialog = xbmcgui.Dialog()
	dialog.textviewer('简介', summary)
'''
@plugin.route('/dbsubject/<subject>')
def dbsubject(subject):
	menus=[]
		try:
		rsp = _http('https://movie.douban.com/subject/'+subject+'/',referer='https://www.douban.com/link2/')
		for match in re.finditer('[\x22\x27]\x2Ftag\x2F(?P<tag>.*?)[\x22\x27]', rsp, re.DOTALL | re.IGNORECASE):
			menus.append({'label': '标签:[COLOR FF00AAFF]%s[/COLOR]' % (match.group('tag')),
					'path':  plugin.url_for('dbmovie',tags=match.group('tag'),sort='0',page='0',addtag='0'),
					'thumbnail':thumb})
		
		return menus
	except Exception,e:
		plugin.notify(str(e))
		return
'''
@plugin.route('/dbsubject/<subject>')
def dbsubject(subject):
	menus=[]
	try:
		rsp = _http('https://api.douban.com/v2/movie/subject/'+subject+'?apikey=0b2bdeda43b5688921839c8ecb20399b',referer='https://www.douban.com/link2/')
		
		#plugin.notify('ok')
		rsp=rsp[rsp.index('{'):]
		#plugin.log.error(rsp)
		minfo = json.loads(rsp[rsp.index('{'):])
		
		year=minfo['year']
		
		comm.moviepoint['group']='db'
		comm.moviepoint['title']=minfo['title']
		comm.moviepoint['thumbnail']=minfo['images']['large'].decode('utf-8')
		
		#summary =''
		#for s,i in enumerate(re.findall(ur'([^\n]{1,28})', minfo['summary'])):
		#	summary=summary+i+'\r\n'
		
		
		#xbmc.log(plugin.url_for('dbsummary', summary=minfo['summary'].encode('utf-8')))
		menus.append({'label':'[COLOR FFFF2222]简介：[/COLOR]%s'%minfo['summary'].encode('utf-8'),
					'path':  plugin.url_for('dbsummary', summary=minfo['summary'].encode('utf-8')),
					'thumbnail':minfo['images']['large'].decode('utf-8')})
		clipandphotos['clips']=[]
		clipandphotos['photos']=[]
		if minfo.has_key('clips'):
			clipandphotos['clips'].extend(minfo['clips'])
		
		if minfo.has_key('bloopers'):
			clipandphotos['clips'].extend(minfo['bloopers'])
		
		if minfo.has_key('photos'):
			clipandphotos['photos'].extend(minfo['photos'])
		

		menus.append({'label':comm.colorize_label('预告片和图片',None,color='32FF94') ,
					'path':  plugin.url_for('dbtrailer'),
					'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'movies.png') ).decode('utf-8')})
		strlist=[]
		strlist.append(minfo['title'])
		strlist.append(minfo['title']+' '+year)
		if minfo.has_key('original_title'):
			#strlist.append(minfo['original_title'])
			strlist.append(minfo['original_title']+' '+year)
		if minfo.has_key('aka'):
			for aka in minfo['aka']:
				if aka.find('(')>=0 and  aka.find(')')>=0:
					aka=aka.replace(aka[ aka.find('('):aka.find(')')+1],'')
				#strlist.append(aka)
				strlist.append(aka+' '+year)
		#去重
		news_strlist = list(set(strlist))
		news_strlist.sort(key=strlist.index)
		
		for sstr in news_strlist:
			context_menu_items=[]
			context_menu_items.append(('搜索'+colorize_label(sstr.encode('UTF-8'), color='00FF00'), 
				'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt',sstr=sstr.encode('UTF-8'),modify='1',otherargs='{}')+')',))
			listitem=ListItem(label='BT:[COLOR FF00FFFF]%s[/COLOR]' % (sstr.encode('utf-8')),
				label2=None, icon=None, thumbnail=xbmc.translatePath( os.path.join( __cwd__, 'magnet.jpg') ).decode('utf-8'),
				path=plugin.url_for('btsearchInit', sstr=sstr.encode('utf-8'), modify='0',ext=comm.moviepoint))
			if len(context_menu_items)>0 and listitem!=None:
				listitem.add_context_menu_items(context_menu_items,False)
				menus.append(listitem)
			
		if minfo.has_key('casts'):
			for cast in minfo['casts']:
				thumb=xbmc.translatePath( os.path.join( __cwd__, 'guest.png') ).decode('utf-8')
				if cast['avatars']:
					if cast['avatars']['medium']:
						thumb=cast['avatars']['medium']
				castname=cast['name'].encode('utf-8')
				
				menus.append({'label': '演员:[COLOR FFFF66AA]%s[/COLOR]' % (castname),
						'path':  plugin.url_for('dbactor', sstr=castname, page=0),
						'context_menu':[('搜索'+colorize_label(castname.encode('UTF-8'), color='00FF00'), 
							'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt,db',sstr=castname.encode('UTF-8'),modify='1',otherargs='{}')+')',)],
						'thumbnail':thumb})
		if minfo.has_key('directors'):
			for director in minfo['directors']:
				thumb=xbmc.translatePath( os.path.join( __cwd__, 'guest.png') ).decode('utf-8')
				if director['avatars']:
					if director['avatars']['medium']:
						thumb=director['avatars']['medium']
				directorname=director['name'].encode('utf-8')
				menus.append({'label': '导演:[COLOR FFFFAA66]%s[/COLOR]' % (directorname),
						'path':  plugin.url_for('dbactor', sstr=directorname, page=0),
						'context_menu':[('搜索'+colorize_label(directorname.encode('UTF-8'), color='00FF00'), 
							'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt,db',sstr=directorname.encode('UTF-8'),modify='1',otherargs='{}')+')',)],
						'thumbnail':thumb})
		if minfo.has_key('year'):
			menus.append({'label': '年代:[COLOR FF00AAFF]%s[/COLOR]' % (minfo['year']),
					'path':  plugin.url_for('dbmovie',tags=minfo['year'],sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
		if minfo.has_key('genres'):
			for genres in minfo['genres']:
				menus.append({'label': '类型:[COLOR FF00AAFF]%s[/COLOR]' % (str(genres)),
						'path':  plugin.url_for('dbmovie',tags=str(genres),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
		if minfo.has_key('countries'):
			for country in minfo['countries']:
				menus.append({'label': '国家:[COLOR FF00AAFF]%s[/COLOR]' % (str(country)),
						'path':  plugin.url_for('dbmovie',tags=str(country),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
		if minfo.has_key('tags'):
			for tag in minfo['tags']:
				menus.append({'label': '标签:[COLOR FF00AAFF]%s[/COLOR]' % (str(tag)),
						'path':  plugin.url_for('dbmovie',tags=str(tag),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
		'''
		rsp = _http('https://movie.douban.com/subject/'+subject+'/',referer='https://www.douban.com/link2/')
		for match in re.finditer('[\x22\x27]\x2Ftag\x2F(?P<tag>.*?)[\x22\x27]', rsp, re.DOTALL | re.IGNORECASE):
			menus.append({'label': '标签:[COLOR FF00AAFF]%s[/COLOR]' % (match.group('tag')),
					'path':  plugin.url_for('dbmovie',tags=match.group('tag'),sort='U',page='0',addtag='0',scorerange='0',year_range='0'),
					'thumbnail':thumb})
		'''
		return menus
	except Exception,e:
		plugin.log.error(str(e))
		return

filters={}


def dbgettag():
	filters['类型标签']=['剧情' , '喜剧' , '动作' , '爱情' , '科幻' , '动画' , '悬疑' , '惊悚' , '恐怖' ,
		'纪录片' , '短片' , '情色' , '同性' , '音乐' , '歌舞' , '家庭' , '儿童' , '传记' , '历史' , '战争' ,
		'犯罪' , '西部' , '奇幻' , '冒险' , '灾难' , '武侠' , '古装' , '运动' , '戏曲' , '黑色电影' ,'女性' , '史诗' , 'cult']
		
	filters['地区标签']=['美国' , '中国大陆' , '香港' , '台湾' , '日本' , '韩国' , '英国' , '法国' , '意大利' , '西班牙' , 
		'德国' , '泰国' , '印度' , '加拿大' , '澳大利亚' , '俄罗斯' , '波兰' , '丹麦' , '瑞典' , '巴西' , '墨西哥' , '阿根廷' ,
		'比利时' , '奥地利' , '荷兰' , '匈牙利' , '土耳其' , '希腊' , '爱尔兰' , '伊朗' , '捷克']
		
	filters['电视剧标签']=['美剧' , '英剧' , '韩剧' , '日剧' , '国产剧' , '港剧' , '台剧' , '泰剧' , '动漫']
	
	filters['年代标签']=['2014' , '2013' , '2012' , '2011' , '2010' , '2009' , '2008' , '2007' , '2006' ,
		'2005' , '2004' , '2003' , '2002' , '2001' , '2000' , '90s' , '80s' , '70s' , '60s' , '50s' , '40s' , '30s']
	curyear=int(time.strftime('%Y',time.localtime(time.time())))
	for intyear in range(2015,curyear+1):
		filters['年代标签'].insert(0, str(intyear))
		
	filters['自定义标签']=plugin.get_setting('dbdeftag').lower().split(',')
	
	sstr=''
	dialog = xbmcgui.Dialog()
	qtyps = ['类型标签','地区标签','电视剧标签','年代标签','自定义标签','手动输入']
	sel = dialog.select('标签类型', qtyps)
	if sel>=0:
		if sel==5:
			mstr = keyboard(u'请输入标签,多个标签用空格隔开')
			if not mstr:
				return
			return mstr
		else:
			sel2=dialog.select('标签类型',filters[qtyps[sel]])
			if sel2==-1: return ''
			return filters[qtyps[sel]][sel2]


@plugin.route('/dbmovie/<tags>/<sort>/<page>/<addtag>/<scorerange>/<year_range>')
def dbmovie(tags='',sort='U',page=0,addtag=0,scorerange='',year_range=''):
	sorttypes=[('近期热门','U'),('标记最多','T'),('评分最高','S'),('最新上映','R')]
	if tags=='0': tags=''
	if sort=='0': sort='U'
	if scorerange=='0': scorerange='0,10'
	curyear=int(time.strftime('%Y',time.localtime(time.time())))
	if year_range=='0': year_range='%d,%d'%(1900,curyear)
	tag=''
	if int(addtag)==1:
		tag=dbgettag()
	
	taglist=[]
	if tags:
		taglist.extend(tags.split(','))
	if tag:
		taglist.extend(tag.split(','))
	#if len(taglist)<1: return;
	tags=''
	for t in taglist:
		tags+=t.strip()+','
	tags=tags.strip(' ,')
	
	if sort=='set':
		dialog = xbmcgui.Dialog()
		sel = dialog.select('排序类型', [q[0] for q in sorttypes])
		if sel==-1: return
		sort=sorttypes[sel][1]
	sorttype=''
	for q in sorttypes:
		if sort==q[1]:
			sorttype=q[0]
			break
	if scorerange=='set':
		sellow=0
		dialog = xbmcgui.Dialog()
		ranges=['0','1','2','3','4','5','6','7','8','9','10']
		sellow = dialog.select('最低评分', ranges[:10])
		if sellow==-1: return
		if sellow>=9:
			scorerange='9,10'
		else:
			selhigh = dialog.select('最高评分', ranges[sellow+1:])
			if selhigh==-1: return
			scorerange='%d,%d'%(sellow,sellow+selhigh+1)
	if year_range=='set':
		sellow=0
		dialog = xbmcgui.Dialog()
		ranges=['2010','2005','2000','1995','1990','1980','1970','1960','1900']
		
		for intyear in range(2011,curyear+1):
			ranges.insert(0, str(intyear))
		sellow = dialog.select('年代起', ranges)
		if sellow==-1: return
		if sellow==0:
			year_range='%d,%d'%(curyear,curyear)
		else:
			yearlow=ranges[sellow]
			ranges=ranges[:sellow+1]
			selhigh = dialog.select('年代止', ranges)
			if selhigh==-1: return
			yearhigh=ranges[selhigh]
			year_range='%s,%s'%(yearlow,yearhigh)
		
	#plugin.notify(tags)
	url='https://movie.douban.com/j/search_subjects?type=movie&tag=%s&sort=%s&page_limit=20&page_start=%s'%(tags.replace(' ','%20').encode('UTF-8'),sort,str(page))
	url='https://movie.douban.com/j/new_search_subjects?'+urllib.urlencode({'tags':tags,'sort':sort,'range':scorerange,'genres':'','start':str(int(page)*20),'year_range':year_range})
	plugin.log.error(url)
	try:
		rsp = _http(url)
		minfo = json.loads(rsp[rsp.index('{'):])
		menus =[]
		for m in minfo['data']:
			context_menu_items=[]
			context_menu_items.append(('搜索'+colorize_label(m['title'].encode('UTF-8'), color='00FF00'), 
				'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt,db',sstr=m['title'].encode('UTF-8'),modify='1',otherargs='{}')+')',))
				
			listitem=ListItem(label='%s[[COLOR FFFF3333]%s[/COLOR]]'%(m['title'],m['rate']),
					thumbnail= m['cover'], 
					path= plugin.url_for('dbsubject', subject=m['id']),)
					
			if len(context_menu_items)>0 and listitem!=None:
				listitem.add_context_menu_items(context_menu_items,False)
				menus.append(listitem)
			
		if len(menus)<=1: 
			plugin.notify('豆瓣标签:无记录')
			return
		tags2='0'
		if tags:
			tags2=tags
		if len(menus)==20:
			menus.append({'label': '下一(第%d)页'%(int(page)+2),
				'path': plugin.url_for('dbmovie',tags=tags2,sort=sort,page=int(page)+1,addtag='0',scorerange=scorerange,year_range=year_range),
				'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'nextpage.png') ).decode('utf-8')})
		menus.insert(0, {'label': '标签:[COLOR FFFF3333]%s[/COLOR]'%(tags),
			'path': plugin.url_for('dbmovie',tags=tags2,sort=sort,page='0',addtag='1',scorerange=scorerange,year_range=year_range)})
		menus.insert(0, {'label': '年代:[COLOR FFFF3333]%s[/COLOR]'%(year_range),
			'path': plugin.url_for('dbmovie',tags=tags2,sort=sort,page='0',addtag='0',scorerange=scorerange,year_range='set')})
		menus.insert(0, {'label': '评分:[COLOR FFFF3333]%s[/COLOR]'%(scorerange),
			'path': plugin.url_for('dbmovie',tags=tags2,sort=sort,page='0',addtag='0',scorerange='set',year_range=year_range)})
		
		menus.insert(0, {'label': '排序:[COLOR FFFF3333]%s[/COLOR]'%(sorttype),
			'path': plugin.url_for('dbmovie',tags=tags2,sort='set',page='0',addtag='0',scorerange=scorerange,year_range=year_range)})
		setthumbnail['set']=True
		plugin.set_content('movies')
		return menus
	except Exception,e:
		plugin.notify(str(e))
		return


def rspmenus(rsp):
	menus=[]
	try:
		rtxt = r'tr class="item".*?nbg"\x20href="(.*?)".*?src="(.*?)"\s+.*?alt="(.*?)".*?class="pl">(.*?)</p>.*?clearfix">(.*?)<span class="pl">'
		patt = re.compile(rtxt, re.S)
		mitems = patt.findall(rsp)
		
		if not mitems: return []
		
		for  s, i in enumerate(mitems):
			rating='-'
			if i[4].find('"rating_nums">')>0:
				rating=i[4][i[4].find('"rating_nums">')+14:i[4].rfind('</span>')]
			menus.append({'label': '{0}. {1}[{2}][{3}]'.format(s, i[2], rating, i[3]),
				 'path': plugin.url_for('dbsubject', subject=i[0][i[0].find('subject')+7:].replace('/','')),
				 'context_menu':[('搜索'+colorize_label(i[2].encode('UTF-8'), color='00FF00'), 
					'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt',sstr=i[2].encode('UTF-8'),modify='1',otherargs='{}')+')',)],
				'thumbnail': i[1],})
				 #'thumbnail': i[1].replace('ipst','lpst').replace('img3.douban.com','img4.douban.com'),})
		return menus
	except:
		return []

@plugin.route('/dbsearch/<sstr>/<page>')
def dbsearch(sstr, page=0):
	if not sstr or sstr=='0':
		sstr = keyboard()
		if not sstr or sstr=='0':
			return
	try:
		sstr=re.sub(r'\s+','',sstr)
		url = 'https://www.douban.com/j/search?q=%s&start=%s&cat=1002' % (sstr, str(int(page)*20))
		rsp = _http(url)
		minfo = json.loads(rsp[rsp.index('{'):])
		menus =[]
		if minfo.has_key('items'):
			for item in minfo['items']:
				rtxt =r'subject%2F(.*?)%2F.*?<img\s+src="(.*?)">.*?}\s*\x29\s*"\s*>(.*?)\s*</a>.*?rating-info">(.*?)</div>'
				patt = re.compile(rtxt, re.S)
				m = patt.search(item)
				if m:
					rat='-'
					ratm = re.search(r'rating_nums">(.*?)</span>', m.group(4), re.DOTALL | re.IGNORECASE)
					if ratm:
						rat = ratm.group(1)

					menus.append({'label': '%s[%s]'%(m.group(3),rat),
						'path': plugin.url_for('dbsubject', subject=m.group(1)),
						'thumbnail': m.group(2),
						'context_menu':[('搜索'+colorize_label(m.group(3).encode('UTF-8'), color='00FF00'), 
							'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt',sstr=m.group(2).encode('UTF-8'),modify='1',otherargs='{}')+')',)],
						})
				else:
					plugin.log.error(item)
	except:
		return
	#try:
	if minfo.has_key('more'):
		if minfo['more']:
			menus.append({
				'label': '下一页',
				'path': plugin.url_for('dbactor', sstr=sstr, page=str(int(page)+1)),
				'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'nextpage.png') ).decode('utf-8'),
				})
	#except: pass
	setthumbnail['set']=True
	return menus

@plugin.route('/dbactor/<sstr>/<page>')
def dbactor(sstr, page=0):
	if not sstr or sstr=='0':
		sstr = keyboard()
		if not sstr or sstr=='0':
			return
	try:
		url = 'https://www.douban.com/j/search?q=%s&start=%s&cat=1002' % (sstr, str(int(page)*20))
		rsp = _http(url)
		minfo = json.loads(rsp[rsp.index('{'):])
		menus =[]
		if minfo.has_key('items'):
			for item in minfo['items']:
				rtxt =r'subject%2F(.*?)%2F.*?<img\s+src="(.*?)">.*?}\s*\x29\s*"\s*>(.*?)\s*</a>.*?rating-info">(.*?)</div>'
				patt = re.compile(rtxt, re.S)
				m = patt.search(item)
				if m:
					rat='-'
					ratm = re.search(r'rating_nums">(.*?)</span>', m.group(4), re.DOTALL | re.IGNORECASE)
					if ratm:
						rat = ratm.group(1)

					menus.append({'label': '%s[%s]'%(m.group(3),rat),
						'path': plugin.url_for('dbsubject', subject=m.group(1)),
						'thumbnail': m.group(2),
						'context_menu':[('搜索'+colorize_label(m.group(3).encode('UTF-8'), color='00FF00'), 
							'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt',sstr=m.group(2).encode('UTF-8'),modify='1',otherargs='{}')+')',)],
						})
				else:
					plugin.log.error(item)
	except:
		return
	#try:
	if minfo.has_key('more'):
		if minfo['more']:
			menus.append({
				'label': '下一页',
				'path': plugin.url_for('dbactor', sstr=sstr, page=str(int(page)+1)),
				'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'nextpage.png') ).decode('utf-8'),
				})
	#except: pass
	setthumbnail['set']=True
	return menus
	'''
	urlpre = 'http://movie.douban.com/subject_search'
	if 'none' in sstr:
		sstr = keyboard()
		if not sstr:
			return
	try:
		url = '%s?search_text=%s&start=%s' % (urlpre ,sstr, str(int(page)*15))
		rsp = _http(url)
		menus=rspmenus(rsp)
	except:return
	
	try:
		count = re.findall(r'class="count">.*?(\d+).*?</span>', rsp)		
		count = int(count[0])
		page = int(page)		
		if (page+1)*15 < count:
			menus.append({
				'label': '下一页',
				'path': plugin.url_for('dbactor', sstr=sstr, page=page+1),
				'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'nextpage.png') ).decode('utf-8'),
				})
	except:
		pass
	setthumbnail['set']=True
	return menus
	'''

@plugin.route('/dbtops')
def dbtops():
	item = [
		{'label': '豆瓣电影新片榜TOP10', 'path': plugin.url_for('dbntop')},
		{'label': '豆瓣电影TOP250', 'path': plugin.url_for('dbtop', page=0)},
		]
		
	types=[['剧情','11'] , ['喜剧','24'] , ['动作','5'] , ['爱情','13'] , ['科幻','17'] , ['动画','25'] , ['悬疑','10'] , ['惊悚','19'] , ['恐怖','20'] , ['纪录','1'] , ['短','23'] , ['情色','6'] , ['同性','26'] , ['音乐','14'] , ['歌舞','7'] , ['家庭','28'] , ['儿童','8'] , ['传记','2'] , ['历史','4'] , ['战争','22'] , ['犯罪','3'] , ['西部','27'] , ['奇幻','16'] , ['冒险','15'] , ['灾难','12'] , ['武侠','29'] , ['古装','30'] , ['运动','18'] , ['黑色影','31']]
	for type in types:
		item.append({'label': type[0]+'片排行', 'path': plugin.url_for('dbtypetop', type=type[1],start=0)})
		lable=type[0]
	return item


@plugin.route('/dbntop')
def dbntop():
	try:
		rsp = _http('http://movie.douban.com/chart')
		menus=rspmenus(rsp)
		setthumbnail['set']=True
		plugin.set_content('movies')
		return menus
	except:return

@plugin.route('/dbtop/<page>')
def dbtop(page):
	page = int(page)
	pc = page * 25
	try:
		rsp = _http('http://movie.douban.com/top250?start={0}'.format(pc))
		mstr = r'class="item".*?href="(.*?)".*?alt="(.*?)" src="(.*?)".*?<p class="">\s+(.*?)</p>'
		mpatt = re.compile(mstr, re.S)
		mitems = mpatt.findall(rsp)
		
		menus = [{'label': '{0}. {1}[{2}]'.format(s+pc+1, i[1], ''.join(
			i[3].replace('&nbsp;', ' ').replace('<br>', ' ').replace(
				'\n', ' ').split(' '))),
				  'path': plugin.url_for('dbsubject', subject=i[0][i[0].find('subject')+7:].replace('/','')),
				  'thumbnail': i[2],
				  'context_menu':[('搜索'+colorize_label(i[1].encode('UTF-8'), color='00FF00'), 
					'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt',sstr=i[1].encode('UTF-8'),modify='1',otherargs='{}')+')',)],
				  #'thumbnail': i[2].replace('ipst','lpst').replace('img3.douban.com','img4.douban.com'),
			 } for s, i in enumerate(mitems)]
		
		if page <9 :
			menus.append({'label': '下一页',
						  'path': plugin.url_for('dbtop', page=page+1),
						  'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'nextpage.png') ).decode('utf-8')})
		
		setthumbnail['set']=True
		plugin.set_content('movies')
		return menus
	except:
		return


@plugin.route('/dbtypetop/<type>/<start>')
def dbtypetop(type='1',start=0):
	url='https://movie.douban.com/j/chart/top_list?type=%s&interval_id=100:90&action=&start=%s&limit=20'%(type,str(start))
	try:
		rsp = _http(url)
		
		#plugin.notify('a')
		minfo = json.loads(rsp[rsp.index('['):])
		
		menus =[]
		plugin.log.error(minfo)
		for m in minfo:
			#plugin.notify(m)
			menus.append({'label': '%s[%s]'%(m['title'],m['score']),
				'path': plugin.url_for('dbsubject', subject=m['id']),
				'thumbnail': m['cover_url'],
				'context_menu':[('搜索'+colorize_label(m['title'].encode('UTF-8'), color='00FF00'), 
					'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt',sstr=m['title'].encode('UTF-8'),modify='1',otherargs='{}')+')',)],
				})
			
		if not len(menus)>1: return
		if len(menus)==20:
			menus.append({'label': '下一页',
				'path': plugin.url_for('dbtypetop',type=type,start=int(start)+20),
				'thumbnail':xbmc.translatePath( os.path.join( __cwd__, 'nextpage.png') ).decode('utf-8')})
		
		setthumbnail['set']=True
		return menus
	except:
		return
