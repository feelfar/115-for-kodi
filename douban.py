# -*- coding: utf-8 -*-
# douban.py
from  __future__  import unicode_literals
import xbmc,xbmcgui,xbmcvfs,os,sys,re,time,json
try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass
from traceback import format_exc
import comm
import lib.six as six
from html.parser import HTMLParser
from lib.six.moves.urllib import parse
plugin = comm.plugin
__cwd__=comm.__cwd__
__resource__ =comm.__resource__
IMAGES_PATH = comm.IMAGES_PATH
__subpath__  = comm.__subpath__
__temppath__  = comm.__temppath__
from commfunc import keyboard,_http,encode_obj,notify
colorize_label=comm.colorize_label
from xbmcswift2 import ListItem

clipandphotos=plugin.get_storage('clipandphotos')

@plugin.route('/dbplaytrailer/<movid>')
def dbplaytrailer(movid):
    videourl=''
    try:
        url='https://movie.douban.com/trailer/'+movid+'/#content'
        rsp= _http(url)
        match = re.search(r'video\s+id.*?source\s+src\x3D[\x27\x22](?P<videourl>.*?)[\x27\x22]', rsp, re.DOTALL | re.MULTILINE)
        if match:
            videourl = match.group('videourl')
        if videourl!='':
            plugin.set_resolved_url(videourl)
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
    
'''
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
    comm.setViewCode='thumbnail'
    return menus
'''

@plugin.route('/dbclips/<subject>')
def dbclips(subject):
    rsp = _http('https://movie.douban.com/subject/%s/trailer#trailer'%subject,referer='https://www.douban.com/link2/')
    rtxt=r'img\s+src\x3D\x22(?P<thumb>[^\s\x22\x3D]*?)\x22.*?\x3Cp\x3E\x3Ca\s+href\x3D\x22.*?trailer\x2F(?P<movid>.*?)\x2F.*?\x3E\s+(?P<movtitle>.*?)\s+\x3C\x2Fa'
    menus=[]
    for clip in re.finditer(rtxt, rsp, re.DOTALL):
        #plugin.log.error(clip.group('thumb'))
        movtitle=HTMLParser().unescape(clip.group('movtitle'))
        menus.append({'label':movtitle,
                'path': plugin.url_for('dbplaytrailer',movid=clip.group('movid')),
                'thumbnail': clip.group('thumb'),
                'is_playable':True, 
                'info_type':'video',
                'info':{'title':movtitle}
                })
    
    comm.setViewCode='thumbnail'
    return menus

@plugin.route('/dbphotos/<subject>/<pictype>/<page>')
def dbphotos(subject,pictype='S',page=0):
    pictypes={'R':'海报','S':'剧照','W':'壁纸'}
    del pictypes[pictype]
    menus=[]
    for key in pictypes:
        menus.append({'label':comm.colorize_label(pictypes[key],None,color='32FF94') ,
                    'path':  plugin.url_for('dbphotos', subject=subject,pictype=key,page=0),
                    'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'picture.png') )})
    url='https://movie.douban.com/subject/%s/photos?type=%s&start=%d'%(subject,pictype,int(page)*30)
    #plugin.log.error(url)
    rsp = _http(url,referer='https://www.douban.com/link2/')
    rtxt=r'\x3Cli.*?data\x2Did.*?img\s+src\x3D\x22(?P<imgurl>[^\s]*?)\x22.*?\x22name\x22\x3E(?P<imgname>.*?)\x3C'
    for photo in re.finditer(rtxt, rsp, re.DOTALL):
        resource_url=''
        limg=photo.group('imgurl')
        limg=limg.replace('/m/','/l/')
        imgname=HTMLParser().unescape(photo.group('imgname').strip())
        menus.append({'label':imgname,
                'path': plugin.url_for('showpic', imageurl=limg),
                #'path':limg,
                #'is_playable':True, 
                #'info_type':'video',
                'properties':{'mimetype':'image/jpeg'},
                'thumbnail': photo.group('imgurl'),
                })
    m = re.search("\x22count\x22.*?(?P<count>[0-9]+)", rsp, re.DOTALL)
    if m:
        count =int( m.group('count'))
        totalpage=int((count-1)/30)
        if int(page)<totalpage:
            menus.append({'label':'下一页','thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') ),
                    'path':  plugin.url_for('dbphotos', subject=subject,pictype=pictype,page=int(page)+1)})
    
    
    comm.setViewCode='thumbnail'
    #notify('dbphotos:'+subject)
    return menus
    
    
@plugin.route('/dbsummary/<summary>')
def dbsummary(summary):
    dialog = xbmcgui.Dialog()
    dialog.textviewer('简介', summary)

@plugin.route('/dbsubject/<subject>')
def dbsubject(subject):
    menus=[]
    try:
        rsp = _http('https://movie.douban.com/subject/'+subject+'/',referer='https://www.douban.com/link2/')
        #plugin.log.error(rsp)
        year=title=title2=thumb=summary=''
        
        m = re.search(r"title\x3E\s*(?P<title>.*?)\s*\x3C\x2Ftitle", rsp, re.DOTALL)
        if m:
            title = m.group("title")
            title=title[0:title.index('(')].strip()
        rtxt = r'dale_movie_subject_top_icon.*?itemreviewed\x22\x3E(?P<title>.*?)\x3C.*?\x22year\x22\x3E(?P<year>.*?)\x3C.*?mainpic.*?img\s+src\x3D\x22(?P<thumb>.*?)\x22'
        m = re.search(rtxt, rsp, re.DOTALL)
        
        if m:
            year=m.group('year').strip(')(')
            title2=HTMLParser().unescape(m.group('title'))
            title2=title2.replace(title,'').strip()
            thumb=m.group('thumb')
            
        rtxt=r'summary.*?\x3E\s*(?P<summary>.*?)\s*\x3C'
        m = re.search(rtxt, rsp, re.DOTALL)
        if m:
            summary=m.group('summary')
        
        rtxt=r'div\s+id\x3D\x22info\x22\x3E\s+(?P<info>.*?)\s+\x3C\x2Fdiv'
        m = re.search(rtxt,rsp, re.DOTALL)
        genres=[]
        areas=[]
        names=[]
       
        if m:
            info=m.group('info')
            m = re.search(r'类型.*?(?P<strs>\x3Cspan.*?span\x3E\s*)\x3Cbr', info, re.DOTALL)
            if m:
                strs = m.group('strs')
                for m in re.finditer("\x3E(?P<gen>[^\x3E\x3C]+?)\x3C\x2Fspan", strs, re.DOTALL):
                    genres.append(m.group('gen'))
            m = re.search(r'制片国家.*?span\x3E\s*(?P<strs>.*?)\x3Cbr', info, re.DOTALL)
            if m:
                strs = m.group('strs')
                for area in strs.split('/'):
                    areas.append(area.strip())
            m = re.search(r'又名.*?span\x3E\s*(?P<strs>.*?)\x3Cbr', info, re.DOTALL)
            if m:
                strs = HTMLParser().unescape(m.group('strs'))
                for othtitle in strs.split('/'):
                    names.append(othtitle.strip())
        celes=[]
                    
        rtxt=r"avatar[^\n]*?background\x2Dimage[^\n]*?url\x28(?P<img>[^\x2C\s]*?)\x29\x22\x3E.*?celebrity\x2F(?P<id>[0-9]+)\x2F.*?name\x22\x3E(?P<name>.*?)\x3C\x2Fa\x3E.*?title\x3D\x22(?P<role>.*?)\x22\x3E"
        for m in re.finditer(rtxt, rsp, re.DOTALL):
             celes.append({'id':m.group('id'),'name':m.group('name'),'img':m.group('img'),'role':m.group('role'),})
             
        tags=[]
        m = re.search("\x22tags-body\x22\x3E.*?\x3C\x2Fdiv\x3E", rsp, re.DOTALL)
        if m:
            tagsg = m.group()
            for m in re.finditer("\x2Ftag\x2F.*?\x3E(?P<tag>.*?)\x3C", tagsg, re.DOTALL):
                tags.append(m.group('tag'))
        
        comm.moviepoint['group']='db'
        comm.moviepoint['title']=title
        comm.moviepoint['thumbnail']=thumb

        menus.append({'label':'[COLOR FFFF2222]简介：[/COLOR]%s'%summary,
                    'path':  plugin.url_for('dbsummary', summary=six.ensure_binary(summary)),
                    'thumbnail':thumb})

        menus.append({'label':comm.colorize_label('预告片',None,color='32FF94') ,
                    'path':  plugin.url_for('dbclips', subject=subject),
                    'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'movies.png') )})
        menus.append({'label':comm.colorize_label('剧照',None,color='32FF94') ,
                    'path':  plugin.url_for('dbphotos', subject=subject,pictype='S',page=0),
                    'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'picture.png') )})
        strlist=[]
        strlist.append(title)
        strlist.append(title+' '+year)
        if title2!='':
            strlist.append(title2+' '+year)
        for aka in names:
            if aka.find('(')>=0 and  aka.find(')')>=0:
                aka=aka.replace(aka[ aka.find('('):aka.find(')')+1],'')
            strlist.append(aka+' '+year)
        #去重
        news_strlist = list(set(strlist))
        news_strlist.sort(key=strlist.index)
        
        for sstr in news_strlist:
            '''
            context_menu_items=[]
            context_menu_items.append(('搜索'+colorize_label(sstr, color='00FF00'), 
                'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(sstr),modify='1',otherargs='{}')+')',))
            listitem=ListItem(label='BT:[COLOR FF00FFFF]%s[/COLOR]' % (six.ensure_text(sstr)),
                label2=None, icon=None,
                thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'magnet.png') ),
                path=plugin.url_for('btsearchInit', sstr=six.ensure_binary(sstr), modify='0',ext=comm.moviepoint))
            if len(context_menu_items)>0 and listitem!=None:
                listitem.add_context_menu_items(context_menu_items)
                menus.append(listitem)
            '''
            sstr = six.ensure_text(sstr).replace('第一季','s01').replace('第二季','s02').replace('第三季','s03').replace('第四季','s04').replace('第五季','s05')\
                .replace('第六季','s06').replace('第七季','s07').replace('第八季','s08').replace('第九季','s09').replace('第十季','s10')\
                .replace('第十一季','s11').replace('第十二季','s12').replace('第十三季','s13').replace('第十四季','s14').replace('第十五季','s15')\
                .replace('第十六季','s16').replace('第十七季','s17').replace('第十八季','s18').replace('第十九季','s19').replace('第二十季','s20')
            menus.append(ListItem(label='搜索:[COLOR FF00FFFF]%s[/COLOR]' % (sstr),
                label2=None, icon=None,
                thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.png') ),
                path=plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(sstr),modify='1',otherargs='{}')))

        
        for cast in celes:
            thumb=cast['img']
            cast['name']+' '+cast['role']
            
            menus.append({'label': '[COLOR FFFF66AA]%s[/COLOR]%s' % (cast['name'],cast['role']),
                    'path':  plugin.url_for('dbactor', sstr=six.ensure_binary(cast['id']),sort='time',page=0),
                    'context_menu':[('搜索'+colorize_label(cast['name'], color='00FF00'), 
                        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,db',sstr=six.ensure_binary(cast['name']),modify='1',otherargs='{}')+')',)],
                    'thumbnail':thumb})
        
        menus.append({'label': '年代:[COLOR FF00AAFF]%s[/COLOR]' % (year),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'tag.png') ),
                    'path':  plugin.url_for('dbmovie',tags=six.ensure_binary(year),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
        for genre in genres:
            menus.append({'label': '类型:[COLOR FF00AAFF]%s[/COLOR]' % (genre),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'tag.png') ),
                    'path':  plugin.url_for('dbmovie',tags=six.ensure_binary(genre),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
        for area in areas:
            menus.append({'label': '地区:[COLOR FF00AAFF]%s[/COLOR]' % (area),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'tag.png') ),
                    'path':  plugin.url_for('dbmovie',tags=six.ensure_binary(area),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
        for tag in tags:
            menus.append({'label': '标签:[COLOR FF00AAFF]%s[/COLOR]' % (tag),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'tag.png') ),
                    'path':  plugin.url_for('dbmovie',tags=six.ensure_binary(tag),sort='U',page='0',addtag='0',scorerange='0',year_range='0')})
        return menus
    except Exception as e:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
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
        
    filters['自定义标签']=six.ensure_text(plugin.get_setting('dbdeftag')).lower().split(',')
    
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
    tags=six.ensure_text(tags)
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
        taglist.append(six.ensure_text(tag))
    #plugin.log.error(str(taglist))
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
    
    #url='https://movie.douban.com/j/search_subjects?type=movie&tag=%s&sort=%s&page_limit=20&page_start=%s'%(tags.replace(' ','%20'),sort,str(page))
    url='https://movie.douban.com/j/new_search_subjects?'+parse.urlencode(encode_obj({'tags':tags,'sort':sort,'range':scorerange,'genres':'','start':str(int(page)*20),'year_range':year_range}))
    try:
        rsp = _http(url)
        minfo = json.loads(rsp[rsp.index('{'):])
        menus =[]
        for m in minfo['data']:
            context_menu_items=[]
            searchtitle = m['title'].replace('第一季','s01').replace('第二季','s02').replace('第三季','s03').replace('第四季','s04').replace('第五季','s05')\
                .replace('第六季','s06').replace('第七季','s07').replace('第八季','s08').replace('第九季','s09').replace('第十季','s10')\
                .replace('第十一季','s11').replace('第十二季','s12').replace('第十三季','s13').replace('第十四季','s14').replace('第十五季','s15')\
                .replace('第十六季','s16').replace('第十七季','s17').replace('第十八季','s18').replace('第十九季','s19').replace('第二十季','s20')
            context_menu_items.append(('搜索'+colorize_label(searchtitle, color='00FF00'), 
                'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,db',sstr=six.ensure_binary(searchtitle),modify='1',otherargs='{}')+')',))
                
            listitem=ListItem(label='%s[[COLOR FFFF3333]%s[/COLOR]]'%(m['title'],m['rate']),
                    thumbnail= m['cover'], 
                    path= plugin.url_for('dbsubject', subject=m['id']),)
                    
            if len(context_menu_items)>0 and listitem!=None:
                listitem.add_context_menu_items(context_menu_items)
                menus.append(listitem)
            
        if len(menus)<=1: 
            notify('豆瓣标签:无记录')
            return
        tags2='0'
        if tags:
            tags2=tags
        if len(menus)==20:
            menus.append({'label': '下一(第%d)页'%(int(page)+2),
                'path': plugin.url_for('dbmovie',tags=six.ensure_binary(tags2),sort=sort,page=int(page)+1,addtag='0',scorerange=scorerange,year_range=year_range),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        menus.insert(0, {'label': '标签:[COLOR FFFF3333]%s[/COLOR]'%(tags),
            'path': plugin.url_for('dbmovie',tags=six.ensure_binary(tags2),sort=sort,page='0',addtag='1',scorerange=scorerange,year_range=year_range)})
        menus.insert(0, {'label': '年代:[COLOR FFFF3333]%s[/COLOR]'%(year_range),
            'path': plugin.url_for('dbmovie',tags=six.ensure_binary(tags2),sort=sort,page='0',addtag='0',scorerange=scorerange,year_range='set')})
        menus.insert(0, {'label': '评分:[COLOR FFFF3333]%s[/COLOR]'%(scorerange),
            'path': plugin.url_for('dbmovie',tags=six.ensure_binary(tags2),sort=sort,page='0',addtag='0',scorerange='set',year_range=year_range)})
        
        menus.insert(0, {'label': '排序:[COLOR FFFF3333]%s[/COLOR]'%(sorttype),
            'path': plugin.url_for('dbmovie',tags=six.ensure_binary(tags2),sort='set',page='0',addtag='0',scorerange=scorerange,year_range=year_range)})
        
        comm.setViewCode='thumbnail'
        return menus
    except Exception as e:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        notify(str(e))
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
                 'context_menu':[('搜索'+colorize_label(i[2], color='00FF00'), 
                    'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(i[2]),modify='1',otherargs='{}')+')',)],
                'thumbnail': i[1],})
                 #'thumbnail': i[1].replace('ipst','lpst').replace('img3.douban.com','img4.douban.com'),})
        return menus
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return []

@plugin.route('/dbsearch/<sstr>/<page>')
def dbsearch(sstr, page=0):
    if not sstr or sstr=='0':
        sstr = keyboard()
        if not sstr or sstr=='0':
            return
    try:
        sstr = re.sub(r'\s+','',sstr)
        #url = 'https://movie.douban.com/j/search_subjects?'+parse.urlencode(encode_obj({'tag':sstr,'page_start':int(page)*20,'cat':1002}))
        url = 'https://www.dianyinggou.com/so/%s/page_%d.html'%(parse.quote_plus(sstr),page+1)
        xbmc.log(msg=url,level=xbmc.LOGERROR)
        rsp = _http(url)
        menus =[]
        rtxt = r'title\x3D[\x22\x27](?P<title>.*?)[\x22\x27].*?\x2Fmov\x2F(?P<dbsubject>.*?)\x2ehtml.*?data\x2Durl\x3D[\x22\x27](?P<img>.*?)[\x22\x27].*?percentW\x3D[\x22\x27](?P<rat>.*?)[\x22\x27]'
        for m in re.finditer(rtxt, rsp, re.DOTALL):
            title=m.group('title')
            rat= float(m.group('rat'))*10
            menus.append({'label': '%s[[COLOR FFFF3333]%s[/COLOR]]'%(title,rat),
                        'path': plugin.url_for('dbsubject', subject=m.group('dbsubject')),
                        'thumbnail': m.group('img'),
                        'context_menu':[('搜索'+colorize_label(title, color='00FF00'), 
                            'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(m.group(2)),modify='1',otherargs='{}')+')',)],
                        })
        '''
        minfo = json.loads(rsp[rsp.index('{'):])
        menus =[]
        if 'items' in minfo:
            for item in minfo['items']:
                rtxt =r'subject%2F(.*?)%2F.*?<img\s+src="(.*?)">.*?}\s*\x29\s*"\s*>(.*?)\s*</a>.*?rating-info">(.*?)</div>'
                patt = re.compile(rtxt, re.S)
                m = patt.search(item)
                if m:
                    rat='-'
                    ratm = re.search(r'rating_nums">(.*?)</span>', m.group(4), re.DOTALL | re.IGNORECASE)
                    if ratm:
                        rat = ratm.group(1)
                    searchtitle = m.group(3).replace('第一季','s01').replace('第二季','s02').replace('第三季','s03').replace('第四季','s04').replace('第五季','s05')\
                        .replace('第六季','s06').replace('第七季','s07').replace('第八季','s08').replace('第九季','s09').replace('第十季','s10')\
                        .replace('第十一季','s11').replace('第十二季','s12').replace('第十三季','s13').replace('第十四季','s14').replace('第十五季','s15')\
                        .replace('第十六季','s16').replace('第十七季','s17').replace('第十八季','s18').replace('第十九季','s19').replace('第二十季','s20')
                    menus.append({'label': '%s[[COLOR FFFF3333]%s[/COLOR]]'%(m.group(3),rat),
                        'path': plugin.url_for('dbsubject', subject=m.group(1)),
                        'thumbnail': m.group(2),
                        'context_menu':[('搜索'+colorize_label(searchtitle, color='00FF00'), 
                            'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(m.group(2)),modify='1',otherargs='{}')+')',)],
                        })
                else:
                    plugin.log.error(item)
    '''
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
    #try:
    
    rtxt = r'(?P<lastpage>[0-9]+)\x2ehtml[\x22\x27]\x3E末页\x3C'
    match = re.search(rtxt, rsp, re.IGNORECASE | re.DOTALL)
    if match:
        lastpage =int(match.group('lastpage'))
        if page<lastpage:
            menus.append({
                'label': '下一页',
                'path': plugin.url_for('dbsearch', sstr=six.ensure_binary(sstr), page=str(int(page)+1)),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') ),
                })
    #except: pass
    comm.setViewCode='thumbnail'
    return menus

@plugin.route('/celephotos/<cele>/<page>')
def celephotos(cele,page=0):
    url='https://movie.douban.com/celebrity/%s/photos/?start=%d&sortby=like&size=a&subtype=a'%(cele,int(page)*30)
    #plugin.log.error(url)
    rsp = _http(url,referer='https://www.douban.com/link2/')
    rtxt=r'img\s+src\x3D\x22(?P<imgurl>[^\s]*?)\x22.*?\x22name\x22\x3E(?P<imgname>.*?)\x3C'
    menus=[]
    for photo in re.finditer(rtxt, rsp, re.DOTALL):
        resource_url=''
        limg=photo.group('imgurl')
        limg=limg.replace('/m/','/l/')
        imgname=HTMLParser().unescape(photo.group('imgname').strip())
        menus.append({'label':imgname,
                'path': plugin.url_for('showpic', imageurl=limg),
                #'path':limg,
                #'is_playable':True, 
                #'info_type':'video',
                'properties':{'mimetype':'image/jpeg'},
                'thumbnail': photo.group('imgurl'),
                })
    m = re.search("\x22count\x22.*?(?P<count>[0-9]+)", rsp, re.DOTALL)
    if m:
        count =int( m.group('count'))
        totalpage=int((count-1)/30)
        if int(page)<totalpage:
            menus.append({'label':'下一页','thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') ),
                    'path':  plugin.url_for('celephotos', cele=cele,page=int(page)+1)})
    
    comm.setViewCode='thumbnail'
    return menus
    
url = 'https://movie.douban.com/celebrity/1274761/photos/'
@plugin.route('/dbactor/<sstr>/<sort>/<page>')
def dbactor(sstr,sort='time',page=0):
    try:
        url = 'https://movie.douban.com/celebrity/%s/' % (sstr)
        rsp = _http(url)
        celename=celeinfo=celeimg=summary=''
        m = re.search(r"\x22nbg\x22\s+title\x3D\x22(?P<celename>.*?)\x22.*?src\x3D\x22(?P<celeimg>.*?)\x22", rsp, re.DOTALL)
        if m:
            celename = m.group("celename")
            celeimg= m.group("celeimg")
        rtxt = r'(?P<celeinfo>\x3Cli\x3E\s+\x3Cspan\x3E性别.+?)\x3C\x2Ful\x3E'
        m = re.search(rtxt, rsp, re.DOTALL)
        if m:
            celeinfo=m.group('celeinfo')
            celeinfo=re.sub(r'\x3C.*?\x3E','',celeinfo)
            celeinfo=re.sub(r'\x3A\s+','\x3A',celeinfo, re.DOTALL)
            celeinfo=celeinfo.replace(' ','')
            celeinfo=re.sub(r'\s+','\r\n',celeinfo, re.DOTALL)
            #plugin.log.error(celename)
        m = re.search(r'影人简介.*?\x22bd\x22\x3E(?P<summary>.*?)\x3C', rsp, re.DOTALL)
        if m:
            summary = m.group("summary")
        m = re.search(r'\x22all\s+hidden\x22\x3E(?P<summary>.*?)\x3C', rsp, re.DOTALL)
        if m:
            summary = m.group("summary")
        menus =[]
        menus.append({'label':'简介：[COLOR FFFF2222]%s[/COLOR]'%celename,
                    'path':  plugin.url_for('dbsummary', summary=six.ensure_binary(celename+celeinfo+summary)),
                    'thumbnail':celeimg})
        menus.append({'label':comm.colorize_label('影人图片',None,color='32FF94') ,
                    'path':  plugin.url_for('celephotos', cele=six.ensure_binary(sstr),page=0),
                    'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'picture.png') )})
        if sort=='time':
            menus.append({'label': '按[COLOR FFFF3333]评分[/COLOR]排序',
                'path': plugin.url_for('dbactor',sstr=six.ensure_binary(sstr),sort='vote',page='0')})
        else:
            menus.append({'label': '按[COLOR FFFF3333]时间[/COLOR]排序',
                'path': plugin.url_for('dbactor',sstr=six.ensure_binary(sstr),sort='time',page='0')})
        url = 'https://movie.douban.com/celebrity/%s/movies?start=%d&format=pic&sortby=%s&' % (sstr,int(page)*10,sort)
        rsp = _http(url)
        rtxt=r'subject\x2F(?P<id>[0-9]+)\x2F.*?img\ssrc\x3D\x22(?P<imgurl>.*?)\x22.*?title\x3D\x22(?P<title>.*?)\x22.*?\x22star\s.*?span\x3E(?P<rate>.*?)\x3C\x2Fdiv'
        for sub in re.finditer(rtxt, rsp, re.DOTALL):
            rate = ''
            mrate=re.search(r'\x3Cspan\x3E(?P<rate>[\x2E0-9]+?)\x3C',sub.group('rate').strip(), re.DOTALL)
            if mrate:
                rate=mrate.group('rate')
            
            context_menu_items=[]
            context_menu_items.append(('搜索'+colorize_label(sub.group('title'), color='00FF00'), 
                'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,db',sstr=six.ensure_binary(sub.group('title')),modify='1',otherargs='{}')+')',))
                
            listitem=ListItem(label='%s[[COLOR FFFF3333]%s[/COLOR]]'%(sub.group('title'),rate),
                    thumbnail= sub.group('imgurl'), 
                    path = plugin.url_for('dbsubject', subject=sub.group('id')),)
                    
            if len(context_menu_items)>0 and listitem!=None:
                listitem.add_context_menu_items(context_menu_items)
                menus.append(listitem)
        
        m = re.search("\x22count\x22.*?(?P<count>[0-9]+)", rsp, re.DOTALL)
        if m:
            count =int( m.group('count'))
            totalpage=int((count-1)/30)
            if int(page)<totalpage:
                menus.append({'label':'下一页','thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') ),
                        'path':  plugin.url_for('dbactor',sstr=six.ensure_binary(sstr),sort=sort,page=int(page)+1)})
        
        comm.setViewCode='thumbnail'
        return menus
        return menus
        
    except Exception as e:
        notify(str(e))
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
    

@plugin.route('/dbtops')
def dbtops():
    item = [
        {'label': '豆瓣电影新片榜TOP10', 'path': plugin.url_for('dbntop')},
        {'label': '豆瓣电影TOP250', 'path': plugin.url_for('dbtop', page=0)},
        ]
        
    dbtypes=[['剧情','11'] , ['喜剧','24'] , ['动作','5'] , ['爱情','13'] , ['科幻','17'] , ['动画','25'] , ['悬疑','10'] , ['惊悚','19'] , ['恐怖','20'] , ['纪录','1'] , ['短','23'] , ['情色','6'] , ['同性','26'] , ['音乐','14'] , ['歌舞','7'] , ['家庭','28'] , ['儿童','8'] , ['传记','2'] , ['历史','4'] , ['战争','22'] , ['犯罪','3'] , ['西部','27'] , ['奇幻','16'] , ['冒险','15'] , ['灾难','12'] , ['武侠','29'] , ['古装','30'] , ['运动','18'] , ['黑色影','31']]
    for dbtype in dbtypes:
        item.append({'label': dbtype[0]+'片排行', 'path': plugin.url_for('dbtypetop', dbtype=dbtype[1],start=0)})
        lable=dbtype[0]
    return item


@plugin.route('/dbntop')
def dbntop():
    try:
        rsp = _http('http://movie.douban.com/chart')
        menus=rspmenus(rsp)
        comm.setViewCode='thumbnail'
        
        return menus
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return

@plugin.route('/dbtop/<page>')
def dbtop(page):
    page = int(page)
    pc = page * 25
    try:
        rsp = _http('http://movie.douban.com/top250?start={0}'.format(pc))
        mstr = r'class="item".*?href="(.*?)".*?alt="(.*?)" src="(.*?)".*?<p class="">\s+(.*?)</p>'
        mpatt = re.compile(mstr, re.S)
        mitems = mpatt.findall(rsp)
        menus = []
        for s, i in enumerate(mitems):
            searchtitle = i[1].replace('第一季','s01').replace('第二季','s02').replace('第三季','s03').replace('第四季','s04').replace('第五季','s05')\
                .replace('第六季','s06').replace('第七季','s07').replace('第八季','s08').replace('第九季','s09').replace('第十季','s10')\
                .replace('第十一季','s11').replace('第十二季','s12').replace('第十三季','s13').replace('第十四季','s14').replace('第十五季','s15')\
                .replace('第十六季','s16').replace('第十七季','s17').replace('第十八季','s18').replace('第十九季','s19').replace('第二十季','s20')
            menus.append({'label': '{0}. {1}[{2}]'.format(s+pc+1, i[1], ''.join(
                i[3].replace('&nbsp;', ' ').replace('<br>', ' ').replace(
                    '\n', ' ').split(' '))),
                      'path': plugin.url_for('dbsubject', subject=i[0][i[0].find('subject')+7:].replace('/','')),
                      'thumbnail': i[2],
                      'context_menu':[('搜索'+colorize_label(searchtitle, color='00FF00'), 
                        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(i[1]),modify='1',otherargs='{}')+')',)],
                      #'thumbnail': i[2].replace('ipst','lpst').replace('img3.douban.com','img4.douban.com'),
                 })
        
        if page <9 :
            menus.append({'label': '下一页',
                          'path': plugin.url_for('dbtop', page=page+1),
                          'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        
        
        comm.setViewCode='thumbnail'
        return menus
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return


@plugin.route('/dbtypetop/<dbtype>/<start>')
def dbtypetop(dbtype='1',start=0):
    url='https://movie.douban.com/j/chart/top_list?type=%s&interval_id=100:90&action=&start=%s&limit=20'%(dbtype,str(start))
    try:
        rsp = _http(url)
        
        #notify('a')
        minfo = json.loads(rsp[rsp.index('['):])
        
        menus =[]
        plugin.log.error(minfo)
        for m in minfo:
            #notify(m)
            menus.append({'label': '%s[%s]'%(m['title'],m['score']),
                'path': plugin.url_for('dbsubject', subject=m['id']),
                'thumbnail': m['cover_url'],
                'context_menu':[('搜索'+colorize_label(m['title'], color='00FF00'), 
                    'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(m['title']),modify='1',otherargs='{}')+')',)],
                })
            
        if not len(menus)>1: return
        if len(menus)==20:
            menus.append({'label': '下一页',
                'path': plugin.url_for('dbtypetop',dbtype=dbtype,start=int(start)+20),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        
        
        comm.setViewCode='thumbnail'
        return menus
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
