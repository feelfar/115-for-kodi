# -*- coding: utf-8 -*-
# douban.py
from  __future__  import unicode_literals
import xbmc,xbmcgui,xbmcvfs,os,sys,re,time,json
try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass
import comm
from urllib import parse
from traceback import format_exc
plugin = comm.plugin
__cwd__=comm.__cwd__
__resource__ =comm.__resource__
IMAGES_PATH = comm.IMAGES_PATH
__subpath__  = comm.__subpath__
__temppath__  = comm.__temppath__
from commfunc import keyboard,_http,url_is_alive,encode_obj,notify
colorize_label=comm.colorize_label
from xbmcswift2 import ListItem

javbusurl = plugin.get_storage('javbusurl')
'''
javbusurl['base']=plugin.get_setting('javbusqb').lower()		
javbusurl['qb']=plugin.get_setting('javbusqb').lower()
javbusurl['bb']=plugin.get_setting('javbusqb').lower()+'/uncensored'
javbusurl['om']=plugin.get_setting('javbusom').lower()
'''


@plugin.route('/javbus')
def javbus():
    if not 'base' in javbusurl.raw_dict():
        javbusurl['base']="https://www.javbus.com"
        getjavbusurl()
    if not url_is_alive(javbusurl['base']):
        notify('网址炸了，请到https://1jubt.top 查看最新地址')
        getjavbusurl()
    #notify(javbusurl['qb'])
    item = [
        {'label': '骑兵片片列表', 'path': plugin.url_for('javlist', qbbb='qb',filtertype='0',filterkey='0',page=1)},
        {'label': '骑兵优优列表', 'path': plugin.url_for('javstarlist', qbbb='qb',page=1)},
        {'label': '骑兵类别筛选', 'path': plugin.url_for('javgernefilter', qbbb='qb')},
        {'label': '骑兵中文片片', 'path': plugin.url_for('javlist', qbbb='qb',filtertype='genre',filterkey='sub',page=1)},
        {'label': '步兵片片列表', 'path': plugin.url_for('javlist', qbbb='bb',filtertype='0',filterkey='0',page=1)},
        {'label': '步兵优优列表', 'path': plugin.url_for('javstarlist', qbbb='bb',page=1)},
        {'label': '步兵类别筛选', 'path': plugin.url_for('javgernefilter', qbbb='bb')},
        {'label': '步兵中文片片', 'path': plugin.url_for('javlist', qbbb='bb',filtertype='genre',filterkey='sub',page=1)},
        {'label': '好雷屋片片列表', 'path': plugin.url_for('javlist', qbbb='om',filtertype='0',filterkey='0',page=1)},
        {'label': '好雷屋优优列表', 'path': plugin.url_for('javstarlist', qbbb='om',page=1)},
        {'label': '好雷屋类别筛选', 'path': plugin.url_for('javgernefilter', qbbb='om')},
        {'label': '片片找找', 'path':  plugin.url_for('searchinit',stypes='jav',sstr='0',modify='0',otherargs='{}')},
        #{'label': '步兵找找', 'path':  plugin.url_for('javlist', qbbb='bb',filtertype='search',filterkey='0',page=1)},
        #{'label': '好雷屋找找', 'path':  plugin.url_for('javlist', qbbb='om',filtertype='search',filterkey='0',page=1)},
        {'label': '更新防屏网址[COLOR FF00FFFF]%s[/COLOR]'%javbusurl['base'], 'path':  plugin.url_for('getjavbusurl')},
    ]
    return item
    
@plugin.route('/getjavbusurl')
def getjavbusurl():
    javbusurl['existmag']='all'
    if not javbusurl['base'] or javbusurl['base'].isspace():
        javbusurl['base']="https://www.javbus.com"
    url=javbusurl['base']
    urltemp=keyboard(text=url,title='输入JAVBus地址')
    if not urltemp or urltemp.isspace():
        return
    url=urltemp.strip().rstrip('/')
    javbusurl['base']=url
    javbusurl['qb']=url
    javbusurl['bb']=url+'/uncensored'
    if not 'om' in javbusurl.raw_dict():
        javbusurl['om']='http://www.javbus.red'
    if url_is_alive(url):
        rsp=_http(url)
        match = re.search(r"href\x3D[\x22\x27](?P<url>(?:http|https)\x3A[\w\x2E\x2F]*?)[\x22\x27]\x3E歐美", rsp, re.IGNORECASE | re.DOTALL)
        if match:
            javbusurl['om']=match.group('url').strip().rstrip('/')
    
@plugin.route('/javmagnet/<qbbb>/<gid>/<uc>')
def javmagnet(qbbb='qb',gid='0',uc='0'):
    menus=[]
    baseurl=javbusurl['base']
    if qbbb=='om':
        baseurl=javbusurl['om']
#try:
    rspmagnet=_http('%s/ajax/uncledatoolsbyajax.php?gid=%s&uc=%s&floor=1'%(baseurl,gid,uc),referer=baseurl)
    #xbmc.log(rspmagnet)
    leechmagnet = re.compile('onmouseover.*?href="(?P<magnet>magnet.*?)">\s*(?P<title>.*?)\s*</a>.*?href.*?">\s*(?P<filesize>.*?)\s*</a>.*?href.*?">\s*(?P<createdate>.*?)\s*</a>',  re.S)
    #if qbbb=='om':
    #	leechmagnet = re.compile(r'onmouseover.*?\x29">\s*(?P<title>.*?)\s*</td>.*?">\s*(?P<filesize>.*?)\s*</td>.*?">\s*(?P<createdate>.*?)\s*</td>.*?href="(?P<magnet>magnet.*?)">',  re.S)
    for match in leechmagnet.finditer(rspmagnet):
        
        magnet=match.group('magnet')
        title=match.group('title')
        title = re.sub("<a\x20.*?>", "|", title)
        filesize=match.group('filesize')
        createdate=match.group('createdate')
        

        filemsg ='大小：'+filesize+'  创建时间：'+createdate
        
        listitem=ListItem(label=comm.colorize_label(title, 'bt'), 
            label2=filesize, icon=None,
            thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'magnet.jpg') ), 
            path=plugin.url_for('execmagnet',
            url=comm.ensure_binary(magnet),title=comm.ensure_binary(title),msg=comm.ensure_binary(filemsg)))
        
        menus.append(listitem)
    return menus
#except:
    notify('自带磁力获取失败')
    return

@plugin.route('/javdetail/<qbbb>/<movieno>/<id>/<title>')
def javdetail(qbbb='qb',movieno='0',id='0',title='0'):
    menus=[]
    url='%s/%s'%(javbusurl['base'],movieno)
    if qbbb=='om':
        url='%s/%s'%(javbusurl['om'],movieno)
    try:
        rsp = _http(url)
        match = re.search("var\x20gid\x20*=\x20*(?P<gid>.*?);.*?var\x20uc\x20=\x20(?P<uc>.*?);", rsp, re.DOTALL | re.MULTILINE)
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        notify('片片信息获取失败')
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
    if match:
        
        gid = match.group('gid')
        uc = match.group('uc')
        if qbbb!='om':
            if uc=='0':qbbb='qb'
            if uc=='1':qbbb='bb'
        menus.append({'label': '[COLOR FF00FFFF]自带磁力[/COLOR]',
                        'path': plugin.url_for('javmagnet', qbbb=qbbb, gid=gid,uc=uc),
                        'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'magnet.jpg') )})
    context_menu_items=[]
    menus.append(ListItem(label='搜索:[COLOR FF00FFFF]%s[/COLOR]' % (id),
            thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.jpg') ), 
            path=plugin.url_for('searchinit',stypes='pan,bt',sstr=comm.ensure_binary(id),modify='1',otherargs='{}'),))
    menus.append(ListItem(label='搜索:[COLOR FF00FFFF]%s[/COLOR]' % (comm.ensure_text(title)),
            thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.jpg') ), 
            path=plugin.url_for('searchinit',stypes='pan,bt',sstr=comm.ensure_binary(title),modify='1',otherargs='{}'),))
    releech='"bigImage"\x20href="(?P<mainimg>.*?)"><'
    leech = re.compile(releech, re.S)
    movieid=''
    
    movieid2=''
    for match in leech.finditer(rsp):
        if qbbb=='qb':
            if movieid=='':
                matchmovid = re.search(r'video/(?P<movieid>.*?)/', match.group('mainimg'), re.DOTALL | re.MULTILINE)
                if matchmovid:
                    movieid = matchmovid.group('movieid')
            if movieid2=='':
                matchmovid2 = re.search(r'cover/(?P<movid2>.+?)_', match.group('mainimg'), re.DOTALL | re.MULTILINE)
                if matchmovid2:
                    movieid2 = matchmovid2.group('movid2')
        
        menus.append({'label':'封面图',
              'path': plugin.url_for('showpic', imageurl=parse.urljoin(javbusurl[qbbb],match.group('mainimg'))),
              'thumbnail':parse.urljoin(javbusurl[qbbb],match.group('mainimg')),})
        comm.moviepoint['group']='javbus'
        comm.moviepoint['title']=title
        comm.moviepoint['thumbnail']=parse.urljoin(javbusurl[qbbb],match.group('mainimg'))
    #notify(movieid+'，'+movieid2)
    releech='</span>\x20<a\x20href="%s/(?P<filter_type>[a-z]+?)/(?P<filter_key>[0-9a-z]+?)">(?P<filter_name>.*?)</a>'%(javbusurl[qbbb])
    leech = re.compile(releech, re.S)
    for match in leech.finditer(rsp):
        filtertype=''
        filterkey=match.group('filter_key')
        if filterkey and filterkey!='0':
            filtername=match.group('filter_name')
            if match.group('filter_type')=='director':
                filtertype= match.group('filter_type')
                filtertypename='导演'
            if match.group('filter_type')=='studio':
                filtertype= match.group('filter_type')
                filtertypename='制作商'
                #if filtername in ['HEYZO','一本道','カリビアンコム','天然むすめ','キャットウォーク']:
                if qbbb=='bb' and filtername not in ['熟女倶楽部','メス豚']:
                    movieid='bb,'+filtername+','+movieno
            if match.group('filter_type')=='label':
                filtertype= match.group('filter_type')
                filtertypename='发行商'
            if match.group('filter_type')=='series':
                filtertype= match.group('filter_type')
                filtertypename='系列'
            if filtertype:
                menus.append({'label':'%s:%s'%(filtertypename,filtername),
                      'path':plugin.url_for('javlist', qbbb=qbbb,filtertype=filtertype,filterkey=filterkey,page=1),
                      'context_menu':[('搜索'+colorize_label(filtername, color='00FF00'), 
                        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,jav',sstr=comm.ensure_binary(filtername),modify='1',otherargs='{}')+')',)]
                      })
    releech='"genre"><a\x20href="%s/(?P<filter_type>[a-z]+?)/(?P<filter_key>[0-9a-z]+?)">(?P<filter_name>.*?)</a>'%(javbusurl[qbbb])
    releech='<a\x20href="%s/(?P<filter_type>[a-z]+?)/(?P<filter_key>[0-9a-z]+?)">(?P<filter_name>.*?)</a>'%(javbusurl[qbbb])
    
    
    leech = re.compile(releech, re.S)
    for match in leech.finditer(rsp):
        filtertype=''
        filterkey=match.group('filter_key')
        if filterkey and filterkey!='0':
            filtername=match.group('filter_name')
            if match.group('filter_type')=='genre':
                filtertype= match.group('filter_type')
                filtertypename='类别'
            if filtertype:
                menus.append({'label':'%s:%s'%(filtertypename,filtername),
                      'path':plugin.url_for('javlist', qbbb=qbbb,filtertype=filtertype,filterkey=filterkey,page=1),
                       'context_menu':[('搜索'+colorize_label(filtername, color='00FF00'), 
                        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,jav',sstr=comm.ensure_binary(filtername),modify='1',otherargs='{}')+')',)]
                      })
    releech='avatar-box.*?href="%s/star/(?P<starid>.*?)">.*?src="(?P<starimg>.*?)".*?<span>(?P<starname>.*?)</span>'%(javbusurl[qbbb])
    if qbbb=='om':
        releech='href="%s/star/(?P<starid>[0-9a-z]{1,10}?)"\s*?target="_blank"><img\s*?src="(?P<starimg>.*?)".*?title.*?title.*?_blank">(?P<starname>.*?)</a>'%(javbusurl[qbbb])
    leech = re.compile(releech, re.S)
    for match in leech.finditer(rsp):
        context_menu_items=[]
        context_menu_items.append(('搜索'+colorize_label(match.group('starname'), color='00FF00'), 
            'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,jav',sstr=comm.ensure_binary(match.group('starname')),modify='1',otherargs='{}')+')',))
            
        listitem=ListItem(label='优优:%s'%(match.group('starname')),
                thumbnail=parse.urljoin(javbusurl[qbbb],match.group('starimg')), 
                path= plugin.url_for('javlist', qbbb=qbbb,filtertype='star',filterkey=match.group('starid'),page=1),)
                
        if len(context_menu_items)>0 and listitem!=None:
            listitem.add_context_menu_items(context_menu_items)
            menus.append(listitem)
        
    releech='sample-box.*?href="(?P<sampleimg>.*?)">.*?src="(?P<thumbimg>.*?)"'
    if qbbb=='om':
        releech='href="(?P<sampleimg>[^"]*?.jpg)"><img\x20src="(?P<thumbimg>[^"]*?thumb.jpg)"'
    leech = re.compile(releech, re.S)
    
    for match in leech.finditer(rsp):
        if qbbb=='qb':
            if movieid=='':
                matchmovid = re.search(r'video/(?P<movieid>.*?)/', match.group('sampleimg'), re.DOTALL | re.MULTILINE)
                if matchmovid:
                    movieid = matchmovid.group('movieid')
        menus.append({'label':'样品图',
              'path': plugin.url_for('showpic', imageurl=parse.urljoin(javbusurl[qbbb],match.group('sampleimg'))),
              'thumbnail':parse.urljoin(javbusurl[qbbb],match.group('thumbimg')),})
    #notify(movieid2)		  
    if movieid=='' and qbbb=='qb' and movieid2!='':
        cururl='https://javzoo.com'
        tellmeurl='https://tellme.pw/avmoo'
        try:
            rsp = _http(tellmeurl)
            matchcururl = re.search(r'strong\x3E\s*\x3Ca\s+href\x3D\x22(?P<cururl>http[s]*\x3A\x2f\x2f[a-zA-Z\x2E]+)\x22', rsp, re.IGNORECASE | re.DOTALL | re.MULTILINE)
            if matchcururl:
                cururl = matchcururl.group('cururl')
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            cururl='https://javzoo.com'
        #url='%s/cn/search/%s'%(cururl,movieid2)
        url='%s/cn/search/%s'%(cururl,movieno)
        try:
            rsp = _http(url)
            #matchmovid = re.search(r'bigImage.*?video/(?P<movieid>.*?)/', rsp, re.DOTALL | re.MULTILINE)
            matchmovid = re.search(r'digital\x2Fvideo\x2F(?P<movieid>.*?)\x2F', rsp, re.DOTALL | re.MULTILINE)
            if matchmovid:
                movieid = matchmovid.group('movieid')
            #leech = re.compile(r'sample-box.*?href="(?P<sampleimg>[^"]*?.jpg)".*?src="(?P<thumbimg>[^"]*?.jpg)"', re.S)
            # for match in leech.finditer(rsp):
                
                # menus.append({'label':'样品图',
                      # 'path': plugin.url_for('showpic', imageurl=match.group('sampleimg')),
                      # 'thumbnail':match.group('thumbimg'),})
                
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            movieid=''
    
    if movieid=='' and qbbb=='qb':
        movieid=id.replace('-','00').lower()
    
    if movieid!='':
        menus.insert(1, {'label':'预告片',
              'path': plugin.url_for('freepv', movieid=comm.ensure_binary(movieid)), 
              'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'movies.png') ),
              'is_playable':True, 
              'info_type':'video',
              'info':{'title':comm.ensure_text(title)}
              })
    comm.setViewCode='thumbnail'
    return menus

@plugin.route('/freepv/<movieid>')
def freepv(movieid=''):
    videourl=''
    subpath=xbmc.translatePath( os.path.join( __cwd__, 'sample.m3u8') )
    
    if movieid[0:3]=='bb,':
        (bb,studio,movid)=comm.ensure_text(movieid).split(',')
        
        if studio=='HEYZO':
            '''
            (unuse,movid2)=movid.split('-')
            videourl=subpath

            videodata=_http('http://hls.heyzo.com/sample/3000/%s/ts.sample.mp4.m3u8'%(movid2),referer='http://www.heyzo.com/js_v2/vendor/jwplayer/7.12.8/jwplayer.flash.swf')
            with open(subpath, "wb") as sampleFile:
                for line in videodata.splitlines():
                    if line[0:1]=='/':
                        sampleFile.write('http://hls.heyzo.com'+line+os.linesep)
                    else:
                        sampleFile.write(line+os.linesep)
            sampleFile.close()
            '''
            (unuse,movid2)=movid.split('-')
            videourl='http://sample.heyzo.com/contents/3000/%s/sample.mp4'%(movid2)
        elif studio=='一本道':	
            videourl='http://smovie.1pondo.tv/sample/movies/%s/1080p.mp4'%(movid)
        elif studio=='カリビアンコム':	
            videourl='https://m.caribbeancom.com/samplemovies/%s/1080p.mp4'%(movid)
        elif studio=='天然むすめ':	
            videourl='http://smovie.10musume.com/sample/movies/%s/1080p.mp4'%(movid)
        elif studio=='パコパコママ':	
            videourl='http://smovie.pacopacomama.com/sample/movies/%s/1080p.mp4'%(movid)
        elif studio=='東京熱':
            
            videodata=_http('https://www.tokyo-hot.com/product/?q=%s'%(movid))
            match = re.search(r'[\x22\x27]\x2Fproduct\x2F(?P<no>[^\s]+?)\x2F[\x22\x27]', videodata, re.DOTALL | re.MULTILINE)
            if match:
                movid2 = match.group('no')
                #notify(movid2)
                videodata=_http('https://www.tokyo-hot.com/product/%s/'%(movid2))
                
                match2 = re.search(r'mp4[\x22\x27]\s+src\s*=\s*[\x22\x27](?P<src>.*?mp4)[\x22\x27]', videodata, re.DOTALL | re.MULTILINE)
                if match2:
                    videourl = match2.group('src')
                        
        #if studio=='キャットウォーク':
        else:
            #videourl='http://www.aventertainments.com/newdlsample.aspx?site=ppv&whichone=ppv/mp4/DL%s.mp4|Referer=http://www.aventertainments.com/product_lists.aspx'%(movid)
            videourl='https://ppvclips03.aventertainments.com/00m3u8/%s/%s.m3u8'%(movid,movid)
            if not url_is_alive(videourl):
                videourl='https://ppvclips03.aventertainments.com/01m3u8/%s/%s.m3u8'%(movid,movid)
        #if not comm.url_is_alive(videourl):
        #	videourl=''

    else:
        for mid in [movieid,movieid[0:-5]+movieid[-3:]]:
            id1c=mid[0:1]
            id3c=mid[0:3]
            for stm in ['_mhb_w','_dmb_w','_dmb_s','_dm_w','_dm_s','_sm_w','_sm_s']:
                videourltemp='https://cc3001.dmm.co.jp/hlsvideo/freepv/%s/%s/%s/%s%s.m3u8'%(id1c,id3c,mid,mid,stm)
                #xbmc.log(videourltemp)
                if url_is_alive(videourltemp):
                    videourl=videourltemp
                    break
            if videourl!='':
                break;
    
    if videourl!='':
        plugin.set_resolved_url(videourl)
    else:
        notify('未找到预告片')
    return

@plugin.route('/chg_existmag/<qbbb>/<filtertype>/<filterkey>')
def chg_existmag(qbbb='qb',filtertype='0',filterkey='0'):

    if javbusurl['existmag']=='all':
        javbusurl['existmag']='mag'
    else:
        javbusurl['existmag']='all'
    return javlist(qbbb=qbbb,filtertype=filtertype,filterkey=filterkey,page=1)

@plugin.route('/javlist/<qbbb>/<filtertype>/<filterkey>/<page>')
def javlist(qbbb='qb',filtertype='0',filterkey='0',page=1):
    if not 'base' in javbusurl.raw_dict():
        getjavbusurl()
    if not 'existmag' in javbusurl.raw_dict():
        javbusurl['existmag']='all'
    if filtertype=='search':
        if not filterkey or filterkey=='0':
            filterkey = keyboard()
            if not filterkey or filterkey=='0':
                return
    filterkey_=filterkey.replace(' ','')
    filterkey_=parse.quote(filterkey_)
    filter=''
    if filtertype!='0':
        if filterkey_!='0':
            filter='/%s/%s'%(filtertype,filterkey_)
        else:
            if filtertype=='search':

                filter='/%s/%s'%(filtertype,filterkey_.replace(' ',''))
            else:
                filter='/'+filtertype
    pagestr=''
    if int(page)>1:
        if filter:
            pagestr='/'+str(page)
        else:
            pagestr='/page/'+str(page)
    url='%s%s%s'%(javbusurl[qbbb],filter,pagestr)
    #if filtertype=='search':
    #    url=url+'&type=1'
    #xbmc.log(url)
    try:
        menus=[]
        if javbusurl['existmag']=='all':
            menus.append({'label':'已显示所有片片',
                'path': plugin.url_for('chg_existmag',qbbb=qbbb,filtertype=filtertype,filterkey=filterkey),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'movies.png') )})
        else:
            menus.append({'label':'已显示有磁片片',
                'path': plugin.url_for('chg_existmag',qbbb=qbbb,filtertype=filtertype,filterkey=filterkey),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'magnet.png') )})
        rsp = _http(url,cookie='existmag='+javbusurl['existmag'])
        
        releech='movie-box.*?href="(?P<detailurl>.*?)".*?src="(?P<imageurl>.*?)".*?title="(?P<title>.*?)".*?<date>(?P<id>.*?)</date>.*?<date>(?P<date>.*?)</date>'
        # if qbbb=='om':
            # releech='"item pull-left".*?href="(?P<detailurl>.*?)".*?src="(?P<imageurl>.*?)".*?"_blank">(?P<title>.*?)</a><br>.*?"item-title">(?P<id>.*?)</span>.*?"item-title">(?P<date>.*?)</span>'
        leech = re.compile(releech, re.S)
        for match in leech.finditer(rsp):
            detailurl=match.group('detailurl')
            movieno=detailurl[detailurl.rfind('/')+1:]
            context_menu_items=[]
            context_menu_items.append(('搜索'+colorize_label(match.group('id'), color='00FF00'), 
                'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=match.group('id'),modify='1',otherargs='{}')+')',))
            thumbimg=parse.urljoin(javbusurl[qbbb],match.group('imageurl'))
            coverimg=thumbimg.replace('thumb','cover').replace('.jpg','_b.jpg')
            listitem=ListItem(label='[[COLOR FFFFFF00]%s[/COLOR]]%s(%s)'%(match.group('id'), match.group('title'), match.group('date')),
                    thumbnail=thumbimg, path= plugin.url_for('javdetail',qbbb=qbbb, movieno=movieno,id=match.group('id'),
                    title=comm.ensure_binary(match.group('title'))),)
            listitem.set_property("Fanart_Image", coverimg)
            #listitem.set_property("Landscape_Image", match.group('imageurl'))
            #listitem.set_property("Poster_Image", match.group('imageurl'))
            #listitem.set_property("Banner_Image", match.group('imageurl'))
            # menus.append({'label':'[[COLOR FFFFFF00]%s[/COLOR]]%s(%s)'%(match.group('id'), match.group('title'), match.group('date')),
                  # 'path': plugin.url_for('javdetail',qbbb=qbbb, movieno=movieno,id=match.group('id'),title=match.group('title')),
                  # 'thumbnail':match.group('imageurl'),})
            if len(context_menu_items)>0 and listitem!=None:
                listitem.add_context_menu_items(context_menu_items)
                menus.append(listitem)
        strnextpage=str(int(page)+1)
        strnextpage='/'+strnextpage+'">'+strnextpage+'</a>'
        if rsp.find(strnextpage)>=0:
            menus.append({'label': '下一页',
                        'path':plugin.url_for('javlist', qbbb=qbbb,filtertype=filtertype,filterkey=filterkey,page=int(page)+1),
                        'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        comm.setViewCode='thumbnail'
        return menus
    except Exception as ex:
        notify('片片列表获取失败'+str(ex))
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return

@plugin.route('/javstarlist/<qbbb>/<page>')
def javstarlist(qbbb='qb',page=1):
    filter='/actresses'
    pagestr=''
    if int(page)>1:
        pagestr='/'+str(page)
    url='%s%s%s'%(javbusurl[qbbb],filter,pagestr)
    try:
        rsp = _http(url)
        releech='avatar-box.*?href="%s/star/(?P<starid>.*?)">.*?src="(?P<starimg>.*?)".*?<span>(?P<starname>.*?)</span>'%(javbusurl[qbbb])		
        # if qbbb=='om':
            # releech=r'star-frame2.*?href="%s/star/(?P<starid>.*?)".*?src="(?P<starimg>.*?)".*?title="(?P<starname>.*?)"'%(javbusurl[qbbb])
        leech = re.compile(releech, re.S)
        menus=[]
        for match in leech.finditer(rsp):
            context_menu_items=[]
            context_menu_items.append(('搜索'+colorize_label(match.group('starname'), color='00FF00'), 
                'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=comm.ensure_binary(match.group('starname')),modify='1',otherargs='{}')+')',))
                
            listitem=ListItem(label='优优:%s'%(match.group('starname')),
                    thumbnail=parse.urljoin(javbusurl[qbbb],match.group('starimg')), path= plugin.url_for('javlist', qbbb=qbbb,filtertype='star',filterkey=match.group('starid'),page=1),)
                    
            if len(context_menu_items)>0 and listitem!=None:
                listitem.add_context_menu_items(context_menu_items)
                menus.append(listitem)
        strnextpage=str(int(page)+1)
        strnextpage='/'+strnextpage+'">'+strnextpage+'</a>'
        if rsp.find(strnextpage)>=0:
            menus.append({'label': '下一页',
                        'path':plugin.url_for('javstarlist', qbbb=qbbb,page=int(page)+1),
                        'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        comm.setViewCode='thumbnail'
        return menus
    except:
        notify('女优列表获取失败')
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return 
'''
def javgernefilter(qbbb='qb',filterkey='-'):
    url=javbusurl[qbbb]+'/genre'
    
    try:
        rsp = _http(url)
        dictgenre={}
        for match in re.finditer("\x2Fgenre\x2F(?P<genreid>.+?)[\x22\x27]\x3E(?P<genrename>.+?)\x3C\x2Fa\x3E", rsp, re.IGNORECASE | re.DOTALL):
            dictgenre[match.group('genreid')] = match.group('genrename')
        filterkeys=filterkey.split('-')
        if filterkey[len(filterkey)-1]=='-':
            #if qbbb!='om':
            releech='<h4>(?P<genregroup>.*?)</h4>.*?"row genre-box">(?P<genres>.*?)</div>'
            leech = re.compile(releech, re.S)
            
            genrelist={}
            genregrouplist=[]
            for match in leech.finditer(rsp):
                genrelist[match.group('genregroup')]= match.group('genres')
                genregrouplist.append(match.group('genregroup'))
            
            dialog = xbmcgui.Dialog()
            
            sel = dialog.select('类别模式', genregrouplist)
            if sel == -1: return
            genregroup=genregrouplist[sel]
            genres=genrelist[genregroup]
            #else:
            #	genres=rsp
            releech = 'href="%s/genre/(?P<genreid>.+?)">(?P<genrename>.+?)</a>'%(javbusurl[qbbb])
            leech = re.compile(releech, re.S)
            genrestemp=[]
            for match in leech.finditer(genres):
                genrestemp.append([match.group('genreid'),match.group('genrename')])
                # menus.append({'label':match.group('genrename'),
                      # 'path':plugin.url_for('javlist', qbbb=qbbb,filtertype='genre',filterkey=match.group('genreid'),page=1),
                      # })
            sel = dialog.select(genregroup, genregrouplist)
            menus.insert(0, {'label': '标签:[COLOR FFFF3333]%s[/COLOR]'%(tags),
                'path': plugin.url_for('dbmovie',tags=comm.ensure_binary(tags2),sort=sort,page='0',addtag='1',scorerange=scorerange,year_range=year_range)})
            return menus
    except:
        notify('类型列表获取失败')
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
'''
@plugin.route('/javgerne/<qbbb>')
def javgernefilter(qbbb='qb'):
    url=javbusurl[qbbb]+'/genre'
    
    try:
        rsp = _http(url)
        menus=[]
        
        #if qbbb!='om':
        releech='<h4>(?P<genregroup>.*?)</h4>.*?"row genre-box">(?P<genres>.*?)</div>'
        leech = re.compile(releech,  re.IGNORECASE | re.DOTALL | re.MULTILINE)
        
        genrelist={}
        genregrouplist=[]
        for match in leech.finditer(rsp):
            genrelist[match.group('genregroup')]= match.group('genres')
            genregrouplist.append(match.group('genregroup'))
        
        dialog = xbmcgui.Dialog()
        
        sel = dialog.select('类别模式', genregrouplist)
        if sel == -1: return
        genres=genrelist[genregrouplist[sel]]
        #else:
        #	genres=rsp
        releech = r'/genre/(?P<genreid>.+?)">(?P<genrename>.+?)</a>'
        leech = re.compile(releech,  re.IGNORECASE | re.DOTALL | re.MULTILINE)
        for match in leech.finditer(genres):
            menus.append({'label':match.group('genrename'),
                  'path':plugin.url_for('javlist', qbbb=qbbb,filtertype='genre',filterkey=match.group('genreid'),page=1),
                  })
        
        return menus
    except:
        notify('类型列表获取失败')
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
