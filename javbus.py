# -*- coding: utf-8 -*-
# douban.py
from  __future__  import unicode_literals
import xbmc,xbmcgui,xbmcvfs,os,sys,re,time,json
try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass
import comm,six
from six.moves.urllib import parse
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
'''
javbusurl['om']=plugin.get_setting('javbusom').lower()

@plugin.route('/javbus')
def javbus():
    if not 'base' in javbusurl.raw_dict():
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
    urls=['https://www.javbus.com']
    for url in plugin.get_setting('javbusfb').lower().split(';'):
        urls.append(url.strip())
        
    '''
    javbusurl['existmag']='all'
    urls=[]
    try:
        javbusfb=plugin.get_setting('javbusfb').lower().split(';')
        rsp = _http(plugin.get_setting('javbusfb').lower())
        #xbmc.log(rsp)
        urlitems=re.compile(r'(http|https)://([a-z0-9\x2E]+)"', re.DOTALL).findall(rsp)
        urlbase=''
        rspbase=''
        
        for  s, url in enumerate(urlitems):
            try:
                urls.append(url[0]+'://'+url[1])
                #urls.append('http://'+url[1])
            except:
                continue
                
        if len(urls)<=0:
            urls.append('https://www.javbus.com')


        
    except:
        notify('JAVBUS网址查询失败')
        #return	
        urls.append('https://www.javbus.com')
        urls.append('https://www.javbus.info')
        urls.append('https://www.javbus.us')
        urls.append('https://www.javbus2.pw')
        urls.append('https://www.javbus3.pw')
    '''
    try:
        dialog = xbmcgui.Dialog()
        sel = dialog.select('网址选择', urls)
        if sel == -1: return
        
        javbusurl['base']=urls[sel]
        javbusurl['qb']=urls[sel]
        javbusurl['bb']=urls[sel]+'/uncensored'
        javbusurl['om']=plugin.get_setting('javbusom').lower()
        '''
        rspbase=_http(javbusurl['base']+'/')
        match = re.search(r'visible-sm-block.*?href="([0-9a-zA-Z\x2E\x2F\x3A]*?)/">歐美', rspbase, re.DOTALL | re.MULTILINE)
        if match:
            javbusurl['om'] = match.group(1)
            notify('JAVBUS网址更新成功！')
        '''
    except:
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        notify('JAVBUS网址更新失败')
        javbusurl['om']=plugin.get_setting('javbusom').lower()
    

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
            url=six.ensure_binary(magnet),title=six.ensure_binary(title),msg=six.ensure_binary(filemsg)))
        
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
    '''
    context_menu_items.append(('搜索'+colorize_label(id, color='00FF00'), 
        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(id),modify='1',otherargs='{}')+')',))
        
    listitem=ListItem(label='BT:[COLOR FF00FFFF]%s[/COLOR]' % (id),
            thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'magnet.jpg') ), 
            path=plugin.url_for('btsearchInit', sstr=id, modify='0'),)
            
    if len(context_menu_items)>0 and listitem!=None:
        listitem.add_context_menu_items(context_menu_items)
        menus.append(listitem)
    title=six.ensure_text(title)
    context_menu_items=[]
    context_menu_items.append((six.ensure_binary('搜索'+colorize_label(title, color='00FF00')), 
        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(title),modify='1',otherargs='{}')+')',))
        
    listitem=ListItem(label='BT:[COLOR FF00FFFF]%s[/COLOR]' % (title),
            thumbnail=xbmc.translatePath( os.path.join( __cwd__, 'magnet.jpg') ), 
            path=plugin.url_for('btsearchInit', sstr=six.ensure_binary(title), modify='0'),)
            
    if len(context_menu_items)>0 and listitem!=None:
        listitem.add_context_menu_items(context_menu_items)
        menus.append(listitem)
    '''
    menus.append(ListItem(label='搜索:[COLOR FF00FFFF]%s[/COLOR]' % (id),
            thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.jpg') ), 
            path=plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(id),modify='1',otherargs='{}'),))
    menus.append(ListItem(label='搜索:[COLOR FF00FFFF]%s[/COLOR]' % (six.ensure_text(title)),
            thumbnail=xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.jpg') ), 
            path=plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(title),modify='1',otherargs='{}'),))
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
              'path': plugin.url_for('showpic', imageurl=match.group('mainimg')),
              'thumbnail':match.group('mainimg'),})
        comm.moviepoint['group']='javbus'
        comm.moviepoint['title']=title
        comm.moviepoint['thumbnail']=match.group('mainimg')
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
                        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,jav',sstr=six.ensure_binary(filtername),modify='1',otherargs='{}')+')',)]
                      })
    releech='"genre"><a\x20href="%s/(?P<filter_type>[a-z]+?)/(?P<filter_key>[0-9a-z]+?)">(?P<filter_name>.*?)</a>'%(javbusurl[qbbb])
    
    
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
                        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,jav',sstr=six.ensure_binary(filtername),modify='1',otherargs='{}')+')',)]
                      })
    releech='avatar-box.*?href="%s/star/(?P<starid>.*?)">.*?src="(?P<starimg>.*?)".*?<span>(?P<starname>.*?)</span>'%(javbusurl[qbbb])
    if qbbb=='om':
        releech='href="%s/star/(?P<starid>[0-9a-z]{1,10}?)"\s*?target="_blank"><img\s*?src="(?P<starimg>.*?)".*?title.*?title.*?_blank">(?P<starname>.*?)</a>'%(javbusurl[qbbb])
    leech = re.compile(releech, re.S)
    for match in leech.finditer(rsp):
        context_menu_items=[]
        context_menu_items.append(('搜索'+colorize_label(match.group('starname'), color='00FF00'), 
            'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,jav',sstr=six.ensure_binary(match.group('starname')),modify='1',otherargs='{}')+')',))
            
        listitem=ListItem(label='优优:%s'%(match.group('starname')),
                thumbnail=match.group('starimg'), 
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
              'path': plugin.url_for('showpic', imageurl=match.group('sampleimg')),
              'thumbnail':match.group('thumbimg'),})
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
              'path': plugin.url_for('freepv', movieid=six.ensure_binary(movieid)), 
              'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'movies.png') ),
              'is_playable':True, 
              'info_type':'video',
              'info':{'title':six.ensure_text(title)}
              })
    comm.setthumbnail=True
    return menus



@plugin.route('/freepv/<movieid>')
def freepv(movieid=''):
    videourl=''
    subpath=xbmc.translatePath( os.path.join( __cwd__, 'sample.m3u8') )
    
    if movieid[0:3]=='bb,':
        (bb,studio,movid)=six.ensure_text(movieid).split(',')
        
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
            
            videodata=_http('http://www.tokyo-hot.com/product/?q=%s'%(movid))
            match = re.search(r'[\x22\x27]\x2Fproduct\x2F(?P<no>[^\s]+?)\x2F[\x22\x27]', videodata, re.DOTALL | re.MULTILINE)
            if match:
                movid2 = match.group('no')
                #notify(movid2)
                videodata=_http('http://www.tokyo-hot.com/product/%s/'%(movid2))
                
                match2 = re.search(r'mp4[\x22\x27]\s+src\s*=\s*[\x22\x27](?P<src>.*?mp4)[\x22\x27]', videodata, re.DOTALL | re.MULTILINE)
                if match2:
                    videourl = match2.group('src')
                        
        #if studio=='キャットウォーク':
        else:
            videourl='http://www.aventertainments.com/newdlsample.aspx?site=ppv&whichone=ppv/mp4/DL%s.mp4|Referer=http://www.aventertainments.com/product_lists.aspx'%(movid)
        #if not comm.url_is_alive(videourl):
        #	videourl=''

    else:
        for mid in [movieid,movieid[0:-5]+movieid[-3:]]:
            id1c=mid[0:1]
            id3c=mid[0:3]
            for stm in ['_dmb_w','_dm_w','_sm_w','_dmb_s','_dm_s','_sm_s']:
                videourltemp='http://cc3001.dmm.co.jp/litevideo/freepv/%s/%s/%s/%s%s.mp4'%(id1c,id3c,mid,mid,stm)
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
    filterkey=filterkey.replace(' ','')
    filterkey=parse.quote(filterkey)
    filter=''
    if filtertype!='0':
        if filterkey!='0':
            filter='/%s/%s'%(filtertype,filterkey)
        
        else:
            if filtertype=='search':
                if not filterkey or filterkey=='0':
                    filterkey = keyboard()
                    if not filterkey or filterkey=='0':
                        return
                filter='/%s/%s'%(filtertype,filterkey.replace(' ',''))
            else:
                filter='/'+filtertype
    pagestr=''
    if int(page)>1:
        if filter:
            pagestr='/'+str(page)
        else:
            pagestr='/page/'+str(page)
    url='%s%s%s'%(javbusurl[qbbb],filter,pagestr)
    if filtertype=='search':
        url=url+'&type=1'
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
            coverimg=match.group('imageurl').replace('thumb','cover').replace('.jpg','_b.jpg')
            listitem=ListItem(label='[[COLOR FFFFFF00]%s[/COLOR]]%s(%s)'%(match.group('id'), match.group('title'), match.group('date')),
                    thumbnail=match.group('imageurl'), path= plugin.url_for('javdetail',qbbb=qbbb, movieno=movieno,id=match.group('id'),
                    title=six.ensure_binary(match.group('title'))),)
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
        comm.setthumbnail=True
        plugin.set_content('movies')
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
                'Container.update('+plugin.url_for('searchinit',stypes='pan,bt',sstr=six.ensure_binary(match.group('starname')),modify='1',otherargs='{}')+')',))
                
            listitem=ListItem(label='优优:%s'%(match.group('starname')),
                    thumbnail=match.group('starimg'), path= plugin.url_for('javlist', qbbb=qbbb,filtertype='star',filterkey=match.group('starid'),page=1),)
                    
            if len(context_menu_items)>0 and listitem!=None:
                listitem.add_context_menu_items(context_menu_items)
                menus.append(listitem)
        strnextpage=str(int(page)+1)
        strnextpage='/'+strnextpage+'">'+strnextpage+'</a>'
        if rsp.find(strnextpage)>=0:
            menus.append({'label': '下一页',
                        'path':plugin.url_for('javstarlist', qbbb=qbbb,page=int(page)+1),
                        'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        comm.setthumbnail=True
        return menus
    except:
        notify('女优列表获取失败')
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
    
@plugin.route('/javgerne/<qbbb>')
def javgernefilter(qbbb='qb'):
    url=javbusurl[qbbb]+'/genre'
    
    try:
        rsp = _http(url)
        menus=[]
        
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
        genres=genrelist[genregrouplist[sel]]
        #else:
        #	genres=rsp
        releech = 'href="%s/genre/(?P<genreid>.+?)">(?P<genrename>.+?)</a>'%(javbusurl[qbbb])
        leech = re.compile(releech, re.S)
        for match in leech.finditer(genres):
            menus.append({'label':match.group('genrename'),
                  'path':plugin.url_for('javlist', qbbb=qbbb,filtertype='genre',filterkey=match.group('genreid'),page=1),
                  })
        return menus
    except:
        notify('类型列表获取失败')
        xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
        return
