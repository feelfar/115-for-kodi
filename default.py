# -*- coding: utf-8 -*-
# default.py
from  __future__  import unicode_literals
import sys

import os,json,xbmc,xbmcgui,xbmcvfs,gzip,re,time,threading,socket,uuid,base64
try:
    xbmc.translatePath = xbmcvfs.translatePath
except AttributeError:
    pass

from datetime import timedelta,datetime,time as dtime
from traceback import format_exc
from xbmcswift2 import Plugin, ListItem
from Cryptodome import Random
from Cryptodome.Hash import MD5
from Cryptodome.Hash import SHA
from Cryptodome.Cipher import PKCS1_OAEP, PKCS1_v1_5
from Cryptodome.PublicKey import RSA

import comm
plugin = comm.plugin
__cwd__=comm.__cwd__
colorize_label=comm.colorize_label
__resource__ =comm.__resource__
IMAGES_PATH = comm.IMAGES_PATH
__subpath__  = comm.__subpath__
__temppath__  = comm.__temppath__

import lib.six as six
from lib.six.moves.urllib import parse
from lib.six.moves.urllib import request
from lib.six.moves import http_cookiejar as cookielib

from commfunc import keyboard,_http,encode_obj,notify

videoexts=plugin.get_setting('videoext').lower().split(',')
musicexts=plugin.get_setting('musicext').lower().split(',')

cookiefile = xbmc.translatePath(os.path.join(__cwd__, 'cookie.dat'))
ids = plugin.get_storage('ids')
renameext = plugin.get_storage('renameext')
cursorttype= plugin.get_storage('cursorttype')
if not 's' in cursorttype.raw_dict():
    cursorttype['s']='0'

import magnet
import douban
import javbus

class QRShower(xbmcgui.WindowDialog):
    def __init__(self):
        # width=self.getWidth() 
        # height=self.getHeight()
        imgsize=360
        bkimg  = xbmc.translatePath( os.path.join( IMAGES_PATH, 'select-bg.png') )
        bkimgControl = xbmcgui.ControlImage(0,0,1280,720, filename = bkimg)
        self.addControl(bkimgControl)
        self.imgControl = xbmcgui.ControlImage((1280-imgsize)//2, (720-imgsize)//2,imgsize, imgsize, filename = '')
        self.addControl(self.imgControl)
        self.labelControl = xbmcgui.ControlLabel((1280-imgsize)//2, (720+imgsize)//2 + 10, imgsize, 10, '请用115手机客户端扫描二维码', alignment = 0x00000002)
        self.addControl(self.labelControl)

    def showQR(self, url):
        socket = request.urlopen( url )
        pngdata = socket.read()
        qrfilepath=xbmc.translatePath( os.path.join( __temppath__, 'qr%s.png'%(uuid.uuid4().hex)) )
        with open(qrfilepath, "wb") as qrFile:
            qrFile.write(pngdata)
        qrFile.close()
        self.imgControl.setImage(qrfilepath)
        self.doModal()
        
    def changeLabel(self, label):
        self.labelControl.setLabel(label)
    def onAction(self,action):
        self.close()
    def onClick(self, controlId):
        self.close()
        
class api_115(object):
    bad_servers = ['fscdnuni-vip.115.com', 'fscdntel-vip.115.com','cdnuni.115.com']
    is_vip=0
    user_name=''
    downcookie=''
    
    def __init__(self, cookiefile):
        self.cookiejar = cookielib.LWPCookieJar()
        if os.path.exists(cookiefile):
            try:
                self.cookiejar.load(
                    cookiefile, ignore_discard=True, ignore_expires=True)
                self.opener = request.build_opener(
                    request.HTTPCookieProcessor(self.cookiejar))
            except:
                xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
                os.remove(cookiefile)
        else:
            self.opener = None
        self.headers = {
            #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
            'Accept-encoding': 'gzip,deflate',
        }
       

    def islogin(self):
        try:
            data = self.urlopen('https://my.115.com/?ct=ajax&ac=nav&_=' + str(time.time()))
            data = json.loads(data[data.index('{'):])
            if data['state'] != True:
                return {'state':False, 'message':data['msg']}
            if 'user_name' in data['data']:
                self.user_name = data['data']['user_name']
            else:
                self.user_name = data['data']['user_id']
            self.is_vip=0
            if 'vip' in data['data']:
                self.is_vip=data['data']['vip']
            
            return True
        except:
            return False
        
    def login(self):
        try:
            self.cookiejar = cookielib.LWPCookieJar()
            self.opener = request.build_opener(request.HTTPCookieProcessor(self.cookiejar))
            login_page = self.urlopen('http://qrcodeapi.115.com/api/1.0/web/1.0/token')
            msgs=json.loads(login_page)
            uid,_t,sign=msgs['data']['uid'],msgs['data']['time'],msgs['data']['sign']
            
        except:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            return {'state':False, 'message':'Login Error'}
        
        qrcode_url='http://qrcodeapi.115.com/api/1.0/web/1.0/qrcode?qrfrom=1&&uid='+str(uid)+'&_t='+str(time.time())
        
        qrShower = QRShower()
        #qrShower.showQR(qrcode_url)
        qthread = threading.Thread(target=qrShower.showQR, args=(qrcode_url,))
        qthread.start()
        
        for i in range(3):
            try:
                data = self.urlopen('http://qrcodeapi.115.com/get/status/?uid='+str(uid)+'&sign='+str(sign)+'&time='+str(_t)+'&_t='+str(int(time.time())))
            except Exception as e:
                qrShower.close()
                qthread.join()
                return {'state':False, 'message':'Login Error'}
            ll = json.loads(data)
            
        qrShower.close()
        for f in os.listdir(__temppath__):
            if re.search(r'^qr.*',f):
                os.remove( os.path.join( __temppath__, f))
        qthread.join()
        try:
            data = self.urlopen('http://passportapi.115.com/app/1.0/web/1.0/login/qrcode',data='app=web&account=' + str(uid))
            if self.islogin():
                if os.path.exists(cookiefile):
                    os.remove(cookiefile)
                self.cookiejar.save(cookiefile, ignore_discard=True)
                return {'state':True, 'user_name':self.user_name,'is_vip':self.is_vip}
            else:
                return  {'state':False, 'message':'Login Error'}
        except:
            return {'state':False, 'message':'Login Error'}
            
    def loginold(self):
        try:
            login_page = self.urlopen('http://passport.115.com/?ct=login&ac=qrcode_token&is_ssl=1')
            msgs=json.loads(login_page)
            uid,_t,sign=msgs['uid'],msgs['time'],msgs['sign']
            
            sessionid_page=self.urlopen('http://msg.115.com/proapi/anonymous.php?ac=signin&user_id='+str(uid)+'&sign='+str(sign)+'&time='+str(_t))
            sessionmsgs=json.loads(sessionid_page)
            sessionid=sessionmsgs['session_id']
            imserver = sessionmsgs['server']
        except:
            return {'state':False, 'message':'Login Error'}
        qrcode_url='http://dgqrcode.115.com/api/qrcode.php?qrfrom=1&&uid='+str(uid)+'&_t='+str(time.time())
        
        qrShower = QRShower()
        #qrShower.showQR(qrcode_url)
        qthread = threading.Thread(target=qrShower.showQR, args=(qrcode_url,))
        qthread.start()
        
        for i in range(2):
            try:
                data = self.urlopen('http://'+imserver+'/chat/r?VER=2&c=b0&s='+str(sessionid)+'&_t='+str(int(time.time())))
            except Exception as e:
                qrShower.close()
                qthread.join()
                return {'state':False, 'message':'Login Error'}
            ll = json.loads(data)
            #ll = eval(data)
            #ll = json.loads(data[data.index('[{'):])
            for l in ll:
                for p in l['p']:
                    if not 'key' in p:
                        #qrShower.changeLabel('请在手机客户端点击登录确认')
                        continue
                    key = p['key']
                    v = p['v']
                    break;
        if not key:
            return {'state':False, 'message':'Login Error'}
        qrShower.close()
        qthread.join()
        try:
            data = self.urlopen('http://fspassport.115.com/?ct=login&ac=qrcode&key=' + key + '&v=' + v)
            if self.islogin():
                if os.path.exists(cookiefile):
                    os.remove(cookiefile)
                self.cookiejar.save(cookiefile, ignore_discard=True)
                return {'state':True, 'user_name':self.user_name,'is_vip':self.is_vip}
            else:
                return  {'state':False, 'message':'Login Error'}
        except:
            return {'state':False, 'message':'Login Error'}
        
        
    def urlopen(self, url,justrsp=False, binary=False, **args):
        if self.opener == None: return '{"state":False, "error":"please Login"}'
        #plugin.log.error(url)
        if 'cookie' in args:
            cookiename,cookievalue=args['cookie'].split('=')
            cook=self.make_cookie(cookiename, cookievalue, '115.com')
            self.cookiejar.set_cookie(cook)
            del args['cookie']
            
        if 'data' in args and type(args['data']) == dict:
            args['data'] = json.dumps(args['data'])
            self.headers['Content-Type'] = 'application/json'
        else:
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        try:
            for key, value in args.items():
                if type(value) == str:
                    args[key]=value.encode()
            headers=self.headers.copy()
            
            if url.find('|')>0:
                url,head=url.split('|')
                params_dict=parse.parse_qsl(head)
                params = dict(params_dict)
                headers.update(params)
            rsp = self.opener.open(
                request.Request(url, headers=headers, **args), timeout=60)
            if justrsp:
                return rsp;
            content = b''
            try:
                self.downcookie=''
                for key,value in rsp.headers.items():
                    if key.lower()=='set-cookie':
                        downcookies = re.findall(r'(?:[0-9abcdef]{20,}|acw_tc)\s*\x3D\s*[0-9abcdef]{20,}', value, re.DOTALL | re.MULTILINE)
                        for downcook in downcookies:
                            self.downcookie+=downcook+';'
            
                if rsp.headers.get('content-encoding', '') == 'gzip':
                    content = gzip.GzipFile(fileobj=six.BytesIO(rsp.read())).read()
                else:
                    content = rsp.read()
                rsp.close()
            except:
                pass
            if binary:
                return content
            else:
                return six.ensure_text(content)
        except Exception as e:
            xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
            plugin.log.error('zzzdebug:%s'%e)
            return ''
            
    def jsonload(self,data):
        try:
            data= data.replace('\n','').replace('\r','')
            data=json.loads(data[data.index('{'):])
            return data
        except:
            return {'state':False,'error':'jsonload error'}
            
    def gettaglist(self):
        data=self.urlopen('https://webapi.115.com/label/list?user_id=&offset=0&limit=11500&sort=create_time&order=desc')
        return self.jsonload(data)
        
    def getfilelist(self,cid,offset,pageitem,star,sorttype,sortasc,typefilter='0',nf='0',search_value=''):        
        if search_value!='' and search_value!='0':
            file_label=''
            match=re.search(r'^tag\s*(?P<tag>[0-9]{10,})$',search_value)
            if match:
                file_label=match.group('tag')
            if file_label:
                data=parse.urlencode(encode_obj({'file_label': file_label,'cid':cid,'aid':'1','limit':str(pageitem),
                            'o':sorttype,'asc':sortasc,'offset':str(offset),'format':'json','date':'','pick_code':'','type':typefilter,'source':''}))
            else:
                data=parse.urlencode(encode_obj({'search_value': search_value,'cid':cid,'aid':'1','limit':str(pageitem),
                            'o':sorttype,'asc':sortasc,'offset':str(offset),'format':'json','date':'','pick_code':'','type':typefilter,'source':''}))
            data=self.urlopen('http://web.api.115.com/files/search?'+data)
        else:
            data = parse.urlencode(encode_obj({'aid': '1','cid':cid,'limit':pageitem,'offset':offset,'type':typefilter,'star':star,'custom_order':'2',
                                'o':sorttype,'asc':sortasc,'nf':nf,'show_dir':'1','format':'json','_':str(int(time.time()))}))
            if sorttype=='file_name':
                data=self.urlopen('http://aps.115.com/natsort/files.php?'+data)
            else:
                data=self.urlopen('http://web.api.115.com/files?'+data)
            #plugin.log.error(data)
        return self.jsonload(data)
    
    def offline(self,url):
        uid = self.getcookieatt('UID')
        uid = uid[:uid.index('_')]
        data = parse.urlencode(encode_obj({'url': url,'uid':uid,'time':str(int(time.time()))}))
        data=self.urlopen("http://115.com/web/lixian/?ct=lixian&ac=add_task_url",data=data)
        data=json.loads(data[data.index('{'):])
        return data
        
    def offline_list(self):
        uid = self.getcookieatt('UID')
        uid = uid[:uid.index('_')]
        page=1
        task=[]
        while True:
            data = parse.urlencode(encode_obj({'page': str(page),'uid':uid,'time':str(int(time.time()))}))
            data=self.urlopen("http://115.com/web/lixian/?ct=lixian&ac=task_lists",data=data)
            data=json.loads(data[data.index('{'):])
            if data['state'] and data['tasks']:
                for item in data['tasks']:
                    task.append(item)
                if data['page_count']>page:
                    page=page+1
                else:
                    break
            else:
                break
        return task
        
    def rename(self,fid,newname):
        data = parse.urlencode(encode_obj({'fid': fid,'file_name':newname}))
        try:
            data=self.urlopen('http://web.api.115.com/files/edit',data=data)
            data= data.replace('\n','').replace('\r','')
            data=json.loads(data[data.index('{'):])
            return data['state']
        except:
            return False
            
    def settag(self,fid,tag):
        data = parse.urlencode(encode_obj({'fid': fid,'file_label':tag}))
        try:
            data=self.urlopen('http://web.api.115.com/files/edit',data=data)
            data= data.replace('\n','').replace('\r','')
            data=json.loads(data[data.index('{'):])
            return data['state']
        except:
            return False
            
    def notecatelist(self):
        data=self.urlopen('https://note.115.com/?ct=note&ac=cate&has_picknews=1')
        return self.jsonload(data)
        
    def noteaddcate(self,cname):
        data = parse.urlencode(encode_obj({'cname': cname,'up_key':'tn__%d_0'%(int(time.time()))}))
        data=self.urlopen('https://note.115.com/?ct=note&ac=addcate',data=data)
        return self.jsonload(data)

    def notegetcateid(self,cname):
        cid=0
        data=self.notecatelist()
        if data['state'] and data['data']:
            for cate in data['data']:
                if cate['cname']==cname:
                    cid=int(cate['cid'])
                    break
        if cid==0:
            data = self.noteaddcate(cname)
            if data['state']:
                cid=int(data['data']['cid'])
        return cid
    
    def notesave(self,cid,nid,title,content):
        data = parse.urlencode(encode_obj({'cid': cid,'nid':nid,'subject':title,'content':content,'is_html':0,'toc_ids':''}))
        data = self.urlopen('https://note.115.com/?ct=note&ac=save',data=data)
        return self.jsonload(data)
        
    def notelist(self,cid,start):
        data = parse.urlencode(encode_obj({'ct':'note','page_size':90,'has_picknews':1,'cid': cid,'keyword':'','start':start,'_':int(time.time())}))
        data = self.urlopen('https://note.115.com/?'+data)
        return self.jsonload(data)
    
    def notedelete(self,nid):
        data = parse.urlencode(encode_obj({'nid': nid}))
        data = self.urlopen('https://note.115.com/?ct=note&ac=delete',data=data)
        return self.jsonload(data)
        
    def notedetail(self,nid):
        data = parse.urlencode(encode_obj({'ct': 'note','nid':nid,'ac':'detail'}))
        data = self.urlopen('https://note.115.com/?'+data)
        return self.jsonload(data)
            
    def notegetcontent(self,cname,notetitle):
        content=''
        cid=self.notegetcateid(cname)
        data=self.notelist(cid=cid,start=0)
        nid=0
        if data['state'] and data['data']:
            for note in data['data']:
                if note['title']==notetitle:
                    nid=int(note['nid'])
                    break
        if nid:
            data = self.notedetail(nid)
            if data['state']:
                content=data['data']['content']
        return content

    def notegetpcurl(self,pc):
        content=''
        cid=self.notegetcateid('pickcodeurl')
        data=self.notelist(cid=cid,start=0)
        nid=0
        nidolds=''
        if data['state'] and data['data']: 
            curtime = int(time.time())
            for note in data['data']:
                if curtime > int(note['create_time'])+60*3600:
                    nidolds+=note['nid']+','
                else:
                    if note['title']==pc:
                        nid=int(note['nid'])
                        break
        if nidolds:
             self.notedelete(nidolds)
        if nid:
            data = self.notedetail(nid)
            if data['state']:
                content=data['data']['content']
        return content
            
            
    def notesavecontent(self,cname,notetitle,content):
        state=False
        cid=self.notegetcateid(cname)
        data=self.notelist(cid=cid,start=0)
        nid=0
        if data['state'] and data['data']:
            for note in data['data']:
                if note['title']==notetitle:
                    nid=int(note['nid'])
                    break
        data = self.notesave(cid=cid,nid=nid,title=notetitle,content=content)
        state = data['state']
        return state
                    
    def notedeleteolds(self,cname):
        state=False
        try:
            cid=self.notegetcateid(cname)
            while True:
                nids=''
                data=self.notelist(cid=cid,start=90)
                state = data['state']
                if data['state'] and data['data']:
                    for note in data['data']:
                        nids=nids+str(note['nid'])+','
                if nids:
                    data = self.notedelete(nid=nids)
                    state = data['state']
                else:
                    break
        except:
            return False
        return state
        
    def getcookiesstr(self):
        cookies=''
        try:
            for cookie in self.cookiejar:
                if cookie.domain.find('115.')>=0:
                    cookies+=str(cookie.name)+'='+str(cookie.value)+';'
            return cookies
        except:
            return ''

    g_kts = [0xF0, 0xE5, 0x69, 0xAE, 0xBF, 0xDC, 0xBF, 0x5A, 0x1A, 0x45, 0xE8, 0xBE, 0x7D, 0xA6, 0x73, 0x88, 0xDE, 0x8F, 0xE7, 0xC4, 0x45, 0xDA, 0x86, 0x94, 0x9B, 0x69, 0x92, 0x0B, 0x6A, 0xB8, 0xF1, 0x7A, 0x38, 0x06, 0x3C, 0x95, 0x26, 0x6D, 0x2C, 0x56, 0x00, 0x70, 0x56, 0x9C, 0x36, 0x38, 0x62, 0x76, 0x2F, 0x9B, 0x5F, 0x0F, 0xF2, 0xFE, 0xFD, 0x2D, 0x70, 0x9C, 0x86, 0x44, 0x8F, 0x3D, 0x14, 0x27, 0x71, 0x93, 0x8A, 0xE4, 0x0E, 0xC1, 0x48, 0xAE, 0xDC, 0x34, 0x7F, 0xCF, 0xFE, 0xB2, 0x7F, 0xF6, 0x55, 0x9A, 0x46, 0xC8, 0xEB, 0x37, 0x77, 0xA4, 0xE0, 0x6B, 0x72, 0x93, 0x7E, 0x51, 0xCB, 0xF1, 0x37, 0xEF, 0xAD, 0x2A, 0xDE, 0xEE, 0xF9, 0xC9, 0x39, 0x6B, 0x32, 0xA1, 0xBA, 0x35, 0xB1, 0xB8, 0xBE, 0xDA, 0x78, 0x73, 0xF8, 0x20, 0xD5, 0x27, 0x04, 0x5A, 0x6F, 0xFD, 0x5E, 0x72, 0x39, 0xCF, 0x3B, 0x9C, 0x2B, 0x57, 0x5C, 0xF9, 0x7C, 0x4B, 0x7B, 0xD2, 0x12, 0x66, 0xCC, 0x77, 0x09, 0xA6]
    g_key_s = [0x29, 0x23, 0x21, 0x5E]
    g_key_l = [0x42, 0xDA, 0x13, 0xBA, 0x78, 0x76, 0x8D, 0x37, 0xE8, 0xEE, 0x04, 0x91]

    def m115_getkey(self,length,key):
        if key != '':
            results = []
            for i in range(length):
                v1=(key[i] + self.g_kts[length * i])&(0xff)
                v2=self.g_kts[length * (length - 1 - i)]
                results.append(v1^v2)
            return results
        if length == 12:
            return self.g_key_l
        else:
            return self.g_key_s
    
    def xor115_enc(self, src, srclen, key, keylen):
        ret = []
        mod4 = srclen % 4
        for i in range(mod4):
            ret.append(src[i] ^ key[i % keylen])
        for i in range(srclen-mod4):
            ret.append(src[i+mod4] ^ key[i % keylen])
        return ret
    
    def m115_sym_encode(self,src, srclen, key1, key2):
        #plugin.log.error('%d %d %d %d %d %d...%d %d'%(src[0],src[1],src[2],src[3],src[4],src[5],src[30],src[31]))
        k1 = self.m115_getkey(4, key1)
        #plugin.log.error(len(k1))
        #plugin.log.error('%d %d ...%d %d'%(k1[0],k1[1],k1[2],k1[3]))

        k2 = self.m115_getkey(12, key2)
        #plugin.log.error(len(k2))
        #plugin.log.error('%d %d ...%d %d'%(k2[0],k2[1],k2[10],k2[11]))
        ret = self.xor115_enc(src, srclen, k1, 4)


        ret.reverse();
        ret = self.xor115_enc(ret, srclen, k2, 12)
        #plugin.log.error(len(ret))
        #plugin.log.error('%d %d %d %d %d %d...%d %d'%(ret[0],ret[1],ret[2],ret[3],ret[4],ret[5],ret[30],ret[31]))
        return ret;
    
    def m115_sym_decode(self,src, srclen, key1, key2):
        k1 = self.m115_getkey(4, key1)
        #plugin.log.error('k1:%d %d %d %d'%(k1[0],k1[1],k1[2],k1[3]))
        
        k2 = self.m115_getkey(12, key2)
        ssss=0
        # for ss in k2:
            # plugin.log.error('k2:%d:%d'%(ssss,ss))
            # ssss+=1
        ret = self.xor115_enc(src, srclen, k2, 12)
        ssss=0
        # for ss in ret:
            # plugin.log.error('ret1:%d:%d'%(ssss,ss))
            # ssss+=1
        ret.reverse()
        ret = self.xor115_enc(ret, srclen, k1, 4)
        return ret
    
    prsa = RSA.importKey('''-----BEGIN RSA PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDR3rWmeYnRClwLBB0Rq0dlm8Mr
PmWpL5I23SzCFAoNpJX6Dn74dfb6y02YH15eO6XmeBHdc7ekEFJUIi+swganTokR
IVRRr/z16/3oh7ya22dcAqg191y+d6YDr4IGg/Q5587UKJMj35yQVXaeFXmLlFPo
kFiz4uPxhrB7BGqZbQIDAQAB
-----END RSA PUBLIC KEY-----''')
    pcipher = PKCS1_v1_5.new(prsa)

    srsa = RSA.importKey('''-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCMgUJLwWb0kYdW6feyLvqgNHmwgeYYlocst8UckQ1+waTOKHFC
TVyRSb1eCKJZWaGa08mB5lEu/asruNo/HjFcKUvRF6n7nYzo5jO0li4IfGKdxso6
FJIUtAke8rA2PLOubH7nAjd/BV7TzZP2w0IlanZVS76n8gNDe75l8tonQQIDAQAB
AoGANwTasA2Awl5GT/t4WhbZX2iNClgjgRdYwWMI1aHbVfqADZZ6m0rt55qng63/
3NsjVByAuNQ2kB8XKxzMoZCyJNvnd78YuW3Zowqs6HgDUHk6T5CmRad0fvaVYi6t
viOkxtiPIuh4QrQ7NUhsLRtbH6d9s1KLCRDKhO23pGr9vtECQQDpjKYssF+kq9iy
A9WvXRjbY9+ca27YfarD9WVzWS2rFg8MsCbvCo9ebXcmju44QhCghQFIVXuebQ7Q
pydvqF0lAkEAmgLnib1XonYOxjVJM2jqy5zEGe6vzg8aSwKCYec14iiJKmEYcP4z
DSRms43hnQsp8M2ynjnsYCjyiegg+AZ87QJANuwwmAnSNDOFfjeQpPDLy6wtBeft
5VOIORUYiovKRZWmbGFwhn6BQL+VaafrNaezqUweBRi1PYiAF2l3yLZbUQJAf/nN
4Hz/pzYmzLlWnGugP5WCtnHKkJWoKZBqO2RfOBCq+hY4sxvn3BHVbXqGcXLnZPvo
YuaK7tTXxZSoYLEzeQJBAL8Mt3AkF1Gci5HOug6jT4s4Z+qDDrUXo9BlTwSWP90v
wlHF+mkTJpKd5Wacef0vV+xumqNorvLpIXWKwxNaoHM=
-----END RSA PRIVATE KEY-----''')
    scipher = PKCS1_v1_5.new(srsa)
    
    def m115_asym_encode(self,src, srclen):
        m = 128 - 11
        ret = bytearray()
        for i in range(int((srclen + m - 1) / m)):
            bsrc=bytes(src[i*m:i*m+m])
            #plugin.log.error(len(bsrc))
            #plugin.log.error('%s %s ...%s %s'%(bsrc[0],bsrc[1],bsrc[30],bsrc[31]))
            rettemp=self.pcipher.encrypt(bsrc)
            #plugin.log.error(len(rettemp))
            ret.extend(rettemp);
            #ret += base64.b64decode(rettemp);
        ret = base64.b64encode(ret)
        return ret

    def m115_asym_decode(self,src, srclen):
        m = 128
        #plugin.log.error(srclen)
        ret = bytearray()
        for i in range(int((srclen + m - 1) / m)):
            rettemp=bytes(src[i*m:i*m+m])
            #dsize = SHA.digest_size
            #sentinel = Random.new().read(16+dsize)
            message=self.scipher.decrypt(rettemp,'')
            #message=self.scipher.decrypt(rettemp,sentinel)
            #digest = SHA.new(message[:-dsize]).digest()
            #if digest==message[-dsize:]:                # Note how we DO NOT look for the sentinel
            #    plugin.log.error("Encryption was correct.")
            #else:
            #    plugin.log.error("Encryption was not correct.")
            ret.extend(message)
        #ssss=0
        #for ss in ret:
        #    plugin.log.error('%d:%d'%(ssss,ord(ss)))
        #    ssss+=1
        return ret
        
    def m115_encode(self,src, tm):
        #plugin.log.error(src)
        key = MD5.new()
        #plugin.log.error(b'tm=%s'%tm)
        key.update(('!@###@#%sDFDR@#@#'%tm).encode())
        bkey = bytearray()
        bkey.extend( key.hexdigest().encode())
        #plugin.log.error(len(bkey))
        #plugin.log.error(key.hexdigest())
        #plugin.log.error('%d %d ...%d %d'%(bkey[0],bkey[1],bkey[30],bkey[31]))
        bsrc = bytearray()
        bsrc.extend(src.encode())
        #plugin.log.error(bsrc)
        tmp = self.m115_sym_encode(bsrc, len(bsrc),bkey, '')
        tmp2 = bkey[0:16]
        tmp2.extend(tmp)
        #plugin.log.error(len(tmp2))
        #plugin.log.error('%d %d %d %d %d %d...%d %d...%d %d'%(tmp2[0],tmp2[1],tmp2[2],tmp2[3],tmp2[4],tmp2[5],tmp2[30],tmp2[31],tmp2[46],tmp2[47]))
        return {
        'data': self.m115_asym_encode(tmp2, len(tmp2)),'key':key.hexdigest()
        }

    def m115_decode(self,src, key):
        bkey1 = bytearray()
        bkey1.extend(key.encode())
        #plugin.log.error('%d %d ...%d %d'%(bkey1[0],bkey1[1],bkey1[30],bkey1[31]))
        tmp = base64.b64decode(src)
        bsrc = bytearray()
        bsrc.extend(tmp)
        tmp = self.m115_asym_decode(bsrc, len(bsrc))
        #plugin.log.error('ch=%s'%len(tmp))
        bkey2 = bytearray()
        bkey2.extend(tmp[0:16])
        #plugin.log.error('key2=%s'%tmp[0:16])
        bsrc2 = bytearray()
        bsrc2.extend(tmp[16:])
        return self.m115_sym_decode(bsrc2, len(tmp) - 16, bkey1,bkey2)
        
    def getfiledownloadurl(self,pc,changeserver='',withcookie=False):
        result = ''
        data=self.urlopen("https://webapi.115.com/files/download?pickcode="+pc+"&_="+str(int(time.time())))
            
        data= self.jsonload(data)
        if data['state']:
            result=data['file_url']
        if not result:
            content=self.notegetpcurl(pc=pc)
            if content:
                result=content
        if not result:
            tm = str(int(int(time.time())))
            pcencode = self.m115_encode((json.dumps({'pickcode': pc})).replace(' ',''),tm)
            #notify(parse.urlencode(encode_obj({'data':pcencode['data']})))
            data = self.urlopen('http://proapi.115.com/app/chrome/downurl?t='+tm,data=parse.urlencode(encode_obj({'data':pcencode['data']})))
            jsondata = json.loads(data[data.index('{'):])
            if jsondata['state'] != True:
                if 'msg' in jsondata:
                    notify('获取文件下载链接出错'+jsondata['msg'])
                    return ''
                if 'error' in jsondata:
                    notify('获取文件下载链接出错'+jsondata['error'])
                    return ''
                else:
                    notify('获取文件下载链接出错')
                    return ''
            decodetmp=self.m115_decode(jsondata['data'], pcencode['key'])
            bdecode = bytearray()
            bdecode.extend(decodetmp)
            jsondata = json.loads(bdecode.decode())
            jsondata=jsondata[list(jsondata.keys())[0]]
            #plugin.log.error(type(jsondata))
        
            if 'url' in jsondata:
                result = jsondata['url']['url']
                self.notesavecontent(cname='pickcodeurl',notetitle=pc,content=result)
        if withcookie:
            cookies=''
            try:
                for cookie in self.cookiejar:
                    if cookie.domain.find('115.')>=0:
                        cookies+=str(cookie.name)+'='+str(cookie.value)+';'
                cookies+=self.downcookie+';'
            except Exception as e:
                xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
                plugin.log.error('zzzdebug:%s'%e)
                os.remove(cookiefile)
            #return result+'|Cookie='+cookies
            #return result+'&'+cookies
            headers=self.headers.copy()
            headers.update({'Cookie':cookies})
            headers.update({'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'})
            headers.update({'Referer': 'https://115.com/?cid=0&offset=0&mode=wangpan'})
            result=result+'|'+parse.urlencode(headers)
        #plugin.log.error(result)
        return result
    
    def oldgetfiledownloadurl(self,pc,changeserver='',withcookie=False):
        result = ''
        data=self.urlopen("https://webapi.115.com/files/download?pickcode="+pc+"&_="+str(int(time.time())))
        if 'Set-Cookie' in data.headers:
            downcookies = re.findall(r"[0-9abcdef]{20,}\s*\x3D\s*[0-9abcdef]{20,}", data.headers['Set-Cookie'], re.DOTALL | re.MULTILINE)
            '''
            downcookies=data.headers['Set-Cookie'].split(',')
            '''
            self.downcookie=''
            for downcook in downcookies:
                self.downcookie+=downcook
            
        data= self.jsonload(data)
        if data['state']:
            result=data['file_url']
        if not result:
            data=self.urlopen("http://proapi.115.com/app/chrome/down?method=get_file_url&pickcode="+pc)
            data= self.jsonload(data)
            if data['state']:
                for value in data['data'].values():
                    if 'url' in value:
                        result = value['url']['url']
                        break
        if not result:
            return ''
        #if result.find('down_group')>0:
            #changeserver=False
        if changeserver!='' and changeserver!='0':
            result = re.sub('(http://)(.*115.com)(.*)', r'\1'+changeserver+r'\3', result)
        
        #if result.find('down_group')>0:
            #return result
        
        if withcookie:
            cookies=''
            try:
                for cookie in self.cookiejar:
                    if cookie.domain.find('115.')>=0:
                        cookies+=str(cookie.name)+'='+str(cookie.value)+';'
                #cookies=parse.quote_plus(cookies)
            except:
                xbmc.log(msg=format_exc(),level=xbmc.LOGERROR)
                os.remove(cookiefile)
            #return result+'|Cookie='+cookies
            #return result+'&'+cookies
            headers=self.headers.copy()
            headers.update({'Cookie':cookies})
            result=result+'|'+parse.urlencode(headers)
        
        return result
        
    def fetch(self,wstream):
        if wstream=='':
            return ''
        try:
            if wstream.headers.get('content-encoding', '') == 'gzip':
                content = gzip.GzipFile(fileobj=six.StringIO(wstream.read())).read()
            else:
                content = wstream.read()
            return content
        except:
            return ''
            
    def make_cookie(self, name, value, domain, path='/'):
        return cookielib.Cookie(
            version=0, 
            name=name, 
            value=value,
            port=None, 
            port_specified=False,
            domain=domain, 
            domain_specified=True, 
            domain_initial_dot=False,
            path=path, 
            path_specified=True,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest=None
        )
    
    def getcookieatt(self, cookiename):
        for cookie in self.cookiejar:
            if cookie.domain.find('115.')>=0:
                if cookie.name==cookiename:
                    return cookie.value
        return ''
        
    def depass(self,ac,ps,co):
        eac=hashlib.sha1(ac).hexdigest()
        eps=hashlib.sha1(ps).hexdigest()
        return hashlib.sha1(hashlib.sha1(eps+eac).hexdigest()+co.upper()).hexdigest()

    def encodes(self):
        prefix = ""
        phpjs=int(random.random() * 0x75bcd15)
        retId = prefix
        retId += self.encodess(int(time.time()),8)
        retId += self.encodess(phpjs, 5)
        return retId

    def encodess(self,seed, reqWidth):
        seed = hex(int(seed))[2:]
        if (reqWidth < len(seed)):
            return seed[len(seed) - reqWidth:]
        if (reqWidth >  len(seed)):
            return (1 + (reqWidth - seed.length)).join('0') + seed
        return seed
        

xl = api_115(cookiefile)

class CaptchaDlg(xbmcgui.WindowDialog):
    def __init__(self):
        # width=self.getWidth()
        # height=self.getHeight()
        bkimg  = xbmc.translatePath( os.path.join( IMAGES_PATH, 'select-bg.png') )
        bkimgControl = xbmcgui.ControlImage(0,0,1280,720, filename = bkimg)
        self.addControl(bkimgControl)
        
        self.capimg = xbmcgui.ControlImage(640-100, 160,200, 50, filename = '')
        self.addControl(self.capimg)
        self.buttonreset = xbmcgui.ControlButton(640+100, 160, 100, 40, 'reset')
        self.addControl(self.buttonreset)
        
        self.capimg1 = xbmcgui.ControlImage(640-100, 210,50, 50, filename = '')
        self.addControl(self.capimg1)
        self.capimg2 = xbmcgui.ControlImage(640-50, 210,50, 50, filename = '')
        self.addControl(self.capimg2)
        self.capimg3 = xbmcgui.ControlImage(640-0, 210,50, 50, filename = '')
        self.addControl(self.capimg3)
        self.capimg4 = xbmcgui.ControlImage(640+50, 210,50, 50, filename = '')
        self.addControl(self.capimg4)
        
        self.capallimg = xbmcgui.ControlImage(640-125,360,250, 100, filename = '')
        self.addControl(self.capallimg)
        
        self.button0 = xbmcgui.ControlButton(640-125+5, 320, 40, 40, '0')
        self.addControl(self.button0)
        self.button1 = xbmcgui.ControlButton(640-75+5, 320, 40, 40, '1')
        self.addControl(self.button1)
        self.button2 = xbmcgui.ControlButton(640-25+5, 320, 40, 40, '2')
        self.addControl(self.button2)
        self.button3 = xbmcgui.ControlButton(640+25+5, 320, 40, 40, '3')
        self.addControl(self.button3)
        self.button4 = xbmcgui.ControlButton(640+75+5, 320, 40, 40, '4')
        self.addControl(self.button4)
        
        self.button5 = xbmcgui.ControlButton(640-125+5, 460, 40, 40, '5')
        self.addControl(self.button5)
        self.button6 = xbmcgui.ControlButton(640-75+5, 460, 40, 40, '6')
        self.addControl(self.button6)
        self.button7 = xbmcgui.ControlButton(640-25+5, 460, 40, 40, '7')
        self.addControl(self.button7)
        self.button8 = xbmcgui.ControlButton(640+25+5, 460, 40, 40, '8')
        self.addControl(self.button8)
        self.button9 = xbmcgui.ControlButton(640+75+5, 460, 40, 40, '9')
        self.addControl(self.button9)
        self.sign = xl.getcookieatt('PHPSESSID')
        if not self.sign:
            data = xl.urlopen('https://captchaapi.115.com/?ac=security_code&type=web',justrsp=True)
            if 'Set-Cookie' in data.headers:
                signs = re.findall(r'[0-9a-z]{26}', data.headers['Set-Cookie'], re.DOTALL | re.MULTILINE)
                if len( signs)>=1:
                    self.sign=signs[0]
        self.showcap()
        
    def showcap(self):
        #capemptyfilepath=xbmc.translatePath( os.path.join( IMAGES_PATH, 'capempty.png') )
        #self.capimg.setImage(capemptyfilepath,useCache=False)
        
        pngdata = xl.urlopen( 'https://captchaapi.115.com/?ct=index&ac=code',cookie='PHPSESSID='+self.sign,binary=True)
        capfilepath=xbmc.translatePath( os.path.join( __temppath__, 'cap%s.png'%(uuid.uuid4().hex)) )
        with open(capfilepath, "wb") as capFile:
            capFile.write(pngdata)
        capFile.close()
        self.capimg.setImage(capfilepath,useCache=False)
        #os.remove(capfilepath)
        #self.capimg.setImage('https://captchaapi.115.com/?ct=index&ac=code',useCache=False)
        pngdata = xl.urlopen( 'https://captchaapi.115.com/?ct=index&ac=code&t=all',cookie='PHPSESSID='+self.sign,binary=True)
        capallfilepath=xbmc.translatePath( os.path.join( __temppath__, 'capall%s.png'%(uuid.uuid4().hex)) )
        with open(capallfilepath, "wb") as capallFile:
            capallFile.write(pngdata)
        capallFile.close()
        self.capallimg.setImage(capallfilepath,useCache=False)
        capemptyfilepath=xbmc.translatePath( os.path.join( IMAGES_PATH, 'capempty.png') )
        self.capimg1.setImage(capemptyfilepath)
        self.capimg2.setImage(capemptyfilepath)
        self.capimg3.setImage(capemptyfilepath)
        self.capimg4.setImage(capemptyfilepath)
        self.caplist=[-1,-1,-1,-1]
        
    def onControl(self,controlId):
        if controlId.getId()==self.buttonreset.getId():
            self.showcap()
            return
            
        selectval=-1
        
        if controlId.getId()==self.button0.getId():
            selectval=0
        if controlId.getId()==self.button1.getId():
            selectval=1
        if controlId.getId()==self.button2.getId():
            selectval=2
        if controlId.getId()==self.button3.getId():
            selectval=3
        if controlId.getId()==self.button4.getId():
            selectval=4
        if controlId.getId()==self.button5.getId():
            selectval=5
        if controlId.getId()==self.button6.getId():
            selectval=6
        if controlId.getId()==self.button7.getId():
            selectval=7
        if controlId.getId()==self.button8.getId():
            selectval=8
        if controlId.getId()==self.button9.getId():
            selectval=9
        if selectval>=0:
            if self.caplist[0]==-1:
                self.caplist[0]=selectval
                pngdata = xl.urlopen('https://captchaapi.115.com/?ct=index&ac=code&t=single&id=%s'%(selectval),cookie='PHPSESSID='+self.sign,binary = True)
                cap1filepath=xbmc.translatePath( os.path.join( __temppath__, 'cap1%s.png'%(uuid.uuid4().hex)) )
                with open(cap1filepath, "wb") as cap1file:
                    cap1file.write(pngdata)
                cap1file.close()
                self.capimg1.setImage(cap1filepath,useCache=False)
            elif self.caplist[1]==-1:
                self.caplist[1]=selectval
                pngdata = xl.urlopen('https://captchaapi.115.com/?ct=index&ac=code&t=single&id=%s'%(selectval),cookie='PHPSESSID='+self.sign,binary = True)
                cap2filepath=xbmc.translatePath( os.path.join( __temppath__, 'cap2%s.png'%(uuid.uuid4().hex)) )
                with open(cap2filepath, "wb") as cap2file:
                    cap2file.write(pngdata)
                cap2file.close()
                self.capimg2.setImage(cap2filepath,useCache=False)
            elif self.caplist[2]==-1:
                self.caplist[2]=selectval
                pngdata = xl.urlopen('https://captchaapi.115.com/?ct=index&ac=code&t=single&id=%s'%(selectval),cookie='PHPSESSID='+self.sign,binary = True)
                cap3filepath=xbmc.translatePath( os.path.join( __temppath__, 'cap3%s.png'%(uuid.uuid4().hex)) )
                with open(cap3filepath, "wb") as cap3file:
                    cap3file.write(pngdata)
                cap3file.close()
                self.capimg3.setImage(cap3filepath,useCache=False)
            elif self.caplist[3]==-1:
                self.caplist[3]=selectval
                pngdata = xl.urlopen('https://captchaapi.115.com/?ct=index&ac=code&t=single&id=%s'%(selectval),cookie='PHPSESSID='+self.sign,binary = True)
                cap4filepath=xbmc.translatePath( os.path.join( __temppath__, 'cap4%s.png'%(uuid.uuid4().hex)) )
                with open(cap4filepath, "wb") as cap4file:
                    cap4file.write(pngdata)
                cap4file.close()
                self.capimg4.setImage(cap4filepath,useCache=False)
                
                code='%s%s%s%s'%(self.caplist[0],self.caplist[1],self.caplist[2],self.caplist[3])
                data = xl.urlopen('https://webapi.115.com/user/captcha',data='code=%s&sign=%s&ac=security_code&type=web'%(code,self.sign))
                data=xl.jsonload(data)
                if data['state']:
                    notify('验证通过')
                    for f in os.listdir(__temppath__):
                        if re.search(r'^cap.*',f):
                            os.remove( os.path.join( __temppath__, f))
                    self.close()
                else:
                    self.showcap()
        

@plugin.route('/login')
def login():
    r=xl.login()
    if r['state']:
        msg='登录成功!当前用户：'+r['user_name']
        if r['is_vip']!=1:
            msg=msg+' 您还不是VIP用户，某些功能可能无法使用，请谅解。'
        notify(msg=msg)
    else:
        notify('登录失败：' + r['message'])
    return

@plugin.route('/setting')
def setting():
    ret= plugin.open_settings()
    return

@plugin.route('/')
def index():
    #plugin.log.error(xl.notecatelist())
    plugin.log.error(str(xl.notedeleteolds('pickcodeurl')))
    
    items = [
        {'label': '网盘文件', 'path': plugin.url_for('getfilelist',cid='0',offset=0,star='0',typefilter=0,searchstr='0',changesort='0'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'icon.png') )},
        {'label': '星标列表', 'path': plugin.url_for('getfilelist',cid='0',offset=0,star='1',typefilter=0,searchstr='0',changesort='0'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'star.png') )},
        {'label': '离线任务列表', 'path': plugin.url_for('offline_list'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'offlinedown.png') )},
        #{'label': '网盘搜索', 'path': plugin.url_for('search',cid='0',mstr='0',offset=0),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.png') )},
        {'label': '网盘标签', 'path': plugin.url_for(pantagsearch,otherargs='{}'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'tag.png') )},
        {'label': '搜索', 'path': plugin.url_for('searchinit',stypes='pan,bt,db,jav',sstr='0',modify='0',otherargs='{}'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.png') )},
        #{'label': '磁力搜索', 'path': plugin.url_for('btsearchother',sstr='0', modify='0'),'thumbnail':xbmc.translatePath(os.path.join( IMAGES_PATH, 'magnet.png'))},
        {'label': '豆瓣标签', 'path': plugin.url_for('dbmovie',tags='0',sort='U',page='0',addtag='0',scorerange='0',year_range='0'),
                            'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'douban.png') )},
        #{'label': '豆瓣电影搜索', 'path': plugin.url_for('dbsearch', sstr='0', page=0),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'moviesearch.png') )},
        {'label': '豆瓣排行榜', 'path': plugin.url_for('dbtops'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'topmovies.png') )},
        {'label': '扫码登入', 'path': plugin.url_for('login'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'scan.png') )},
        {'label': '设置', 'path': plugin.url_for('setting'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'setup.png') )},
        #{'label': 'captcha', 'path': plugin.url_for('captcha')},
    ]
    if str(plugin.get_setting('javbus'))=='true':
        items.insert(7, {'label': 'javbus', 'path': plugin.url_for('javbus'),'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'javbus.png') )})
    sortasc=str(plugin.get_setting('sortasc'))
    comm.setthumbnail=True
    return items

@plugin.route('/btsearchother')
def btsearchother():
    comm.moviepoint['group']='other'
    comm.moviepoint['thumbnail']='0'
    return magnet.btsearchInit(sstr='0', modify='0')

def stypesearch(liststypes,sstr,dictotherargs):
    xbmc.log(msg=sstr,level=xbmc.LOGERROR)
    stypedict={'pan':'网盘搜索','bt':'磁力搜索','db':'豆瓣搜索','jav':'JAVBUS搜索'}
    stype=''
    if len(liststypes)==1:
        stype=liststypes[0]
    else:
        dialog = xbmcgui.Dialog()
        selectlist=[]
        for st in liststypes:
            selectlist.append((st,stypedict[st]))
        sel = dialog.select('搜索'+colorize_label(sstr, color='FFFF00'), [q[1] for q in selectlist])
        if sel>=0:
            stype= selectlist[sel][0]
    if stype=='pan':
        cid='0'
        if 'cid' in dictotherargs:
            cid=dictotherargs['cid']
        #return pansearch(cid=cid,mstr=sstr,offset=0)
        return getfilelist(cid=cid,offset=0,star='0',typefilter='0',searchstr=sstr,changesort='0')
    elif stype=='bt':
        return magnet.btsearchInit(sstr=sstr, modify='0')
    elif stype=='db':
        return douban.dbsearch(sstr=sstr, page=0)
    elif stype=='jav':
        qbbblist=[('骑兵','qb'),('步兵','bb'),('好雷屋','om')]
        dialog = xbmcgui.Dialog()
        sel = dialog.select('JAVBUS 搜索'+colorize_label(sstr, color='FFFF00'),[q[0] for q in qbbblist])
        if sel>=0:
            qbbb= qbbblist[sel][1]
            return javbus.javlist(qbbb=qbbb,filtertype='search',filterkey=sstr,page=1)

def selectstr(sstr):
    #strlist=re.split(r'[\s\x2E\x5B\x5D\x28\x29\x3C\x3E\x5F]+', sstr)
    strlist=re.split(r'[\s\u0021-\u002C\u002E-\u002F\u003A-\u0040\u005B-\u0060\u007B-\u007E\uFF01-\uFF0F\uFF1A-\uFF20\uFF5B-\uFF65]+', sstr)
    #notify(strlist)
    strsel=''
    dialog = xbmcgui.Dialog()
    sel=999
    while sel>0:
        sellist=['选择：'+colorize_label(strsel, color='FFFF00')]+strlist
        sel = dialog.select('选择字符串',sellist)
        if sel>0:
            strsel=strsel+' '+strlist[sel-1]
            strsel=strsel.strip()
            strlist.pop(sel-1)
        if sel==-1:
            strsel=''
    return strsel

def gettaglist(color=True):
    taglist=[]
    data=xl.gettaglist()
    if data['state']:
        fllist=sorted( data['data']['list'],key=lambda k:k['sort'],reverse=True)
        for tag in fllist:
            name=tag['name']
            if color and len(tag['color'])==7:
                name=colorize_label(tag['name'], color=tag['color'][1:])
            taglist.append([name,tag['id']])
    return taglist
    
@plugin.route('/pantagsearch/<otherargs>')
def pantagsearch(otherargs):
    tagid=''
    taglist=gettaglist()
    dialog = xbmcgui.Dialog()
    sel = dialog.select('选择标签',[k[0] for k in taglist])
    
    if sel!=-1:
        tagid='tag'+taglist[sel][1]
    if tagid:
        cid='0'
        dictotherargs=json.loads(otherargs)
        if 'cid' in dictotherargs:
            cid=dictotherargs['cid']
        return getfilelist(cid=cid,offset=0,star='0',typefilter='0',searchstr=tagid,changesort='0')
    return

@plugin.route('/searchinit/<stypes>/<sstr>/<modify>/<otherargs>')
def searchinit(stypes,sstr,modify,otherargs):
    if not 'strlist' in comm.searchvalues.raw_dict():
        comm.searchvalues['strlist']=[]
    sstr=six.ensure_text(sstr)
    sstr=sstr.strip()
    liststypes=stypes.split(',')
    if str(plugin.get_setting('javbus'))!='true':
        if 'jav' in liststypes:
            liststypes.remove('jav')
    dictotherargs=json.loads(otherargs)
    if not isinstance(dictotherargs,dict):
        dictotherargs={}
    if sstr and sstr!='0' and modify=='0':
        comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if six.ensure_binary(e)!=six.ensure_binary(sstr)]
        comm.searchvalues['strlist'].append(sstr)
        comm.searchvalues.sync()
        return stypesearch(liststypes,sstr,dictotherargs)
    else:
        if modify=='1':
            if sstr=='0': sstr=''
            newsstr = keyboard(text=sstr).strip()
            if not newsstr:
                comm.searchvalues.sync()
                return
            comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if e!=sstr]
            comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if e!=newsstr]
            comm.searchvalues['strlist'].append(newsstr)
            comm.searchvalues.sync()
            return stypesearch(liststypes,newsstr,dictotherargs)
            #comm.searchvalues['strlist'].append(newsstr)
            '''
            if not sstr:
                comm.searchvalues['strlist'].append(newsstr)
                comm.searchvalues.sync()
                return stypesearch(liststypes,newsstr,dictotherargs)
            else:
                updataurl=plugin.url_for('searchinit',stypes=stypes,sstr=six.ensure_binary(newsstr),modify='0',otherargs=otherargs)
                #xbmc.log(msg=updataurl,level=xbmc.LOGERROR)
                #xbmc.executebuiltin('Container.update(%s)'%updataurl)
                xbmc.executebuiltin('RunPlugin(%s)'%updataurl)
                #xbmc.executebuiltin('Container.update(RunPlugin(%s))'%updataurl)'''
        if modify=='4':
            newsstr=selectstr(sstr)
            if not newsstr:
                comm.searchvalues.sync()
                return
            newsstr = keyboard(text=newsstr).strip()
            if not newsstr:
                comm.searchvalues.sync()
                return
            comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if e!=sstr]
            comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if e!=newsstr]
            comm.searchvalues['strlist'].append(newsstr)
            comm.searchvalues.sync()
            return stypesearch(liststypes,newsstr,dictotherargs)
            #comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if e!=newsstr]
            #updataurl=plugin.url_for('searchinit',stypes=stypes,sstr=six.ensure_binary(newsstr),modify='1',otherargs=otherargs)
            #xbmc.executebuiltin('Container.update(%s)'%updataurl)
            #xbmc.executebuiltin('RunPlugin(%s)'%updataurl)
        if modify=='2':
            comm.searchvalues['strlist']= [e for e in comm.searchvalues['strlist'] if e!=sstr]
            xbmc.executebuiltin('Container.Refresh()')
            #return
        if modify=='3':
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('清空搜索关键字', '是否删除所有搜索关键字')
            if ret:
                comm.searchvalues['strlist']=[]
        items=[]
        items.append({'label': colorize_label('网盘标签搜索', color='00FFFF'), 'path': plugin.url_for('pantagsearch',otherargs=otherargs)})
        items.append({'label': colorize_label('添加搜索关键字', color='00FF00'), 'path': plugin.url_for('searchinit',stypes=stypes,sstr='0',modify='1',otherargs=otherargs)})
        for strvalue in comm.searchvalues['strlist'][::-1]:
            context_menu_items=[]
            listitem=ListItem(label=strvalue, label2=None, icon=None, thumbnail=None, 
                    path=plugin.url_for('searchinit',stypes=stypes,sstr=six.ensure_binary(strvalue),modify='0',otherargs=otherargs))
            context_menu_items.append(('编辑关键字'+colorize_label(six.ensure_text(strvalue), color='0000FF'), 'RunPlugin('+plugin.url_for('searchinit',stypes=stypes,sstr=six.ensure_binary(strvalue),modify='1',otherargs=otherargs)+')',))
            context_menu_items.append(('删除关键字'+colorize_label(six.ensure_text(strvalue), color='FF0000'), 'RunPlugin('+plugin.url_for('searchinit',stypes=stypes,sstr=six.ensure_binary(strvalue),modify='2',otherargs=otherargs)+')',))
            if len(context_menu_items)>0:
                listitem.add_context_menu_items(context_menu_items)
            items.append(listitem)
        if len(comm.searchvalues['strlist'])>0:
            items.append({'label': colorize_label('清空搜索关键字', color='FF0000'), 'path': plugin.url_for('searchinit',stypes=stypes,sstr='0',modify='3',otherargs=otherargs)})
        comm.searchvalues.sync()
        comm.setthumbnail=False
        return items

@plugin.route('/pansearch/<cid>/<mstr>/<offset>')
def pansearch(cid,mstr,offset):
    if not mstr or mstr=='0':
        mstr = keyboard()
        if not mstr:
            return
    data=getfilelistdata(cid,offset,'0','0',searchstr=mstr)
    if data['state']:
        #playlistvideo = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #playlistvideo.clear()
        
        imagecount=0
        items=[]
        
        milkname='115'
        
        if str(plugin.get_setting('genm3u8'))=='true':
            items.append({'label': '生成M3U8文件', 'path': plugin.url_for('m3u8',cid=cid,offset=offset,star='0',name=milkname)})
        for item in data['data']:
            listitem=getListItem(item,mstr)
            if listitem!=None:
                #if listitem.playable:
                    #playlistvideo.add(listitem.get_path(), listitem.as_xbmc_listitem())
                items.append(listitem)
                if 'ms' in item:
                    imagecount+=1
        if data['count']>int(offset)+int(pageitem):
            items.append({'label': colorize_label('下一页', 'next'),
                'path': plugin.url_for('pansearch',cid=cid,mstr=mstr,offset=str(int(offset)+int(pageitem))),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        #plugin.set_content('movies')
        
        if imagecount >= 10 and imagecount * 2 > len(items):
            #plugin.set_content('images')
            comm.setthumbnail=True
        return items
    else:
        notify(msg='数据获取失败,错误信息:'+six.ensure_text(data['error']))
        login()
        return
        
def is_subtitle(ext):
    return ext.lower() in ['srt', 'idx', 'sub', 'ssa', 'smi', 'ass']

def getListItem(item,pathname=''):
    #plugin.log.error(item)
    context_menu_items=[]
    context_menu_items.append(('搜索'+colorize_label(item['n'], color='00FF00'), 
        'Container.update('+plugin.url_for('searchinit',stypes='pan,bt,db,jav',sstr=six.ensure_binary(item['n']),modify='4',otherargs='0')+')',))
    #context_menu_items.append(('搜索'+colorize_label(item['n'], color='00FF00'), 
    #    'RunPlugin('+plugin.url_for('searchinit',stypes='pan,bt,db,jav',sstr=six.ensure_binary(item['n']),modify='4',otherargs='0')+')',))
    if 'sha' in item:
        context_menu_items.append(('用'+colorize_label('浏览器','dir')+'打开代理链接', 
                'RunPlugin('+plugin.url_for('shellopen',pc=item['pc'],fname=six.ensure_binary(item['n']))+')',))
        if 'iv' in item:
            isiso='1'
            if 'vdi' in item:
                if item['vdi']>=1:
                    isiso='0'
            listitem=ListItem(label=colorize_label(item['n'], 'video'), label2=None, icon=None, thumbnail=None, 
                    path=plugin.url_for('play',pc=item['pc'],name=six.ensure_binary(item['n']),iso=isiso))
            
            listitem.set_info('video', {'title':item['n'],'size': item['s']})
            #listitem.as_xbmc_listitem().setContentLookup(False)
            listitem.set_is_playable('true')
            context_menu_items.append(('FFMpeg转码下载', 
                'RunPlugin('+plugin.url_for('ffmpeg',pc=item['pc'],name=six.ensure_binary(item['n']))+')',))
            
        elif 'ms' in item:
            #imgurl=getimgurl(item['pc'])
            listitem=ListItem(label=colorize_label(item['n'], 'image'), label2=None, icon=None, thumbnail=xbmc.translatePath(os.path.join( IMAGES_PATH, 'picture.png')),
                    path=plugin.url_for('playimg',pc=item['pc'],name=six.ensure_binary(item['n'])))
            #listitem=ListItem(label=colorize_label(item['n'], 'image'), label2=None, icon=None, thumbnail=None, path=imgurl)
            #listitem.set_info('pictures', {"Title": item['n'] } )
            listitem.playable=False


        elif item['ico'] in videoexts:
            listitem=ListItem(label=colorize_label(item['n'], 'video'), label2=None, icon=None, thumbnail=None, path=plugin.url_for('play',pc=item['pc'],name=six.ensure_binary(item['n']),iso='1'))
            listitem.set_info('video', {'title':item['n'],'size': item['s']})
            #listitem.as_xbmc_listitem().setContentLookup(False)
            listitem.set_is_playable('true')
            
        elif  item['ico'] in musicexts:
            listitem=ListItem(label=colorize_label(item['n'], 'audio'), label2=None, icon=None, thumbnail=None, path=plugin.url_for('play',pc=item['pc'],name=six.ensure_binary(item['n']),iso='1'))
            listitem.set_info('audio', {'title':item['n'],'size': item['s']})
            listitem.playable=True

        elif item['ico']=='torrent':
            listitem=ListItem(label=colorize_label(item['n'], 'bt'), label2=None, icon=None, thumbnail=None, path=plugin.url_for('offline_bt',sha1=item['sha']))
        
        elif str(plugin.get_setting('showallfiles'))=='true':
            listitem=ListItem(label=item['n'], label2=None, icon=None, thumbnail=None)
        else:
            listitem=None
            
        if is_subtitle(item['ico']):            
            if item['ico'].lower()=='idx' or item['ico'].lower()=='sub':
                subname=(item['n'][:item['n'].rfind('.')]+'.idx_sub')
                if subname in subcache.raw_dict():
                    comm.subcache[subname][item['ico'].lower()]=item['pc']
                else:
                    comm.subcache[subname]={}
                    comm.subcache[subname][item['ico'].lower()]=item['pc']
            else:
                comm.subcache[item['n']]=item['pc']
            comm.subcache.sync()
        
        if 'u' in item and  listitem!=None:
            listitem.set_thumbnail(item['u'])
            
        if 'cid' in item:
            locateurl=plugin.url_for('getfilelist',cid=item['cid'],offset=0,star='0',typefilter=0,searchstr='0',changesort='0')
            context_menu_items.append((colorize_label('定位到所在目录','menu'), 'Container.update(%s)'%locateurl,))
        if str(plugin.get_setting('panedit'))=='true':
            if listitem!=None and 'cid' in item and 'fid' in item:
                warringmsg='是否删除文件:'+item['n']
                deleteurl=plugin.url_for('deletefile',pid=item['cid'],fid=item['fid'],warringmsg=six.ensure_binary(warringmsg))
                context_menu_items.append((colorize_label('删除',color='FF0044'), 'RunPlugin('+deleteurl+')',))
    else:
        listitem=ListItem(label=colorize_label(item['n'], 'dir'), label2=None, icon=None, thumbnail=None, path=plugin.url_for('getfilelist',cid=item['cid'],offset=0,star='0',typefilter=0,searchstr='0',changesort='0'))
        
        if 'pid' in item:
            locateurl=plugin.url_for('getfilelist',cid=item['pid'],offset=0,star='0',typefilter=0,searchstr='0',changesort='0')
            context_menu_items.append((colorize_label('定位到所在目录','menu'), 'Container.update(%s)'%locateurl,))
            
        if str(plugin.get_setting('panedit'))=='true':
            if 'cid' in item and 'pid' in item:
                warringmsg='是否删除目录及其下所有文件:'+item['n']
                #listitem.add_context_menu_items([('删除', 'RunPlugin('+plugin.url_for('deletefile',pid=item['pid'],fid=item['cid'],warringmsg=warringmsg)+')',)])
                deleteurl=plugin.url_for('deletefile',pid=item['pid'],fid=item['cid'],warringmsg=six.ensure_binary(warringmsg))
                context_menu_items.append((colorize_label('删除',color='FF0044'), 'RunPlugin('+deleteurl+')',))
    fl=','
    if 'fid' in item:
        fid=item['fid']
    else:
        fid=item['cid']
    if 'fl' in item and  listitem!=None:
        for tag in item['fl']:
            fl=fl+tag['id']+','
            if len(tag['color'])==7:
                
                #listitem.label=listitem.label
                listitem.label=six.ensure_binary(colorize_label('●', color=tag['color'][1:]))+six.ensure_binary(listitem.label)
    context_menu_items.append((colorize_label('设置标签',color='00CCCC'), 'RunPlugin('+plugin.url_for('settag',fid=fid,fllist=fl)+')',))        
    if 'm' in item and  listitem!=None:
        listitem.set_property('is_mark',str(item['m']))
        listitem.label=six.ensure_binary(colorize_label('★', 'star'+six.text_type(item['m'])))+six.ensure_binary(listitem.label)
        
                
        if str(plugin.get_setting('panedit'))=='true':
            context_menu_items.append((colorize_label('重命名',color='0044FF'), 'RunPlugin('+plugin.url_for('rename',fid=fid,filename=six.ensure_binary(item['n']))+')',))
            context_menu_items.append((colorize_label('移动..',color='00FF44'), 'RunPlugin('+plugin.url_for('move',fid=fid,filename=six.ensure_binary(item['n']))+')',))
        if str(item['m'])=='0':
            #listitem.add_context_menu_items([('星标', 'RunPlugin('+plugin.url_for('mark',fid=fid,mark='1')+')',)])
            context_menu_items.append((colorize_label('星标',color='FFFF00'), 'RunPlugin('+plugin.url_for('mark',fid=fid,mark='1')+')',))
        else:
            #listitem.add_context_menu_items([('取消星标', 'RunPlugin('+plugin.url_for('mark',fid=fid,mark='0')+')',)])
            context_menu_items.append(('取消星标', 'RunPlugin('+plugin.url_for('mark',fid=fid,mark='0')+')',))
    
            

    if len(context_menu_items)>0 and listitem!=None:
        listitem.add_context_menu_items(context_menu_items)
    return listitem

@plugin.route('/deletefile/<pid>/<fid>/<warringmsg>')
def deletefile(pid,fid,warringmsg):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno(colorize_label('删除警告',color='FF0044'), warringmsg)
    if ret:
        try:
            data = parse.urlencode(encode_obj({'pid': pid,'fid':fid}))
            data=xl.urlopen('http://web.api.115.com/rb/delete',data=data)
            data= data.replace('\n','').replace('\r','')
            data=json.loads(data[data.index('{'):])
            #notify(data,delay=50000)
            if data['state']:
                xbmc.executebuiltin('Container.Refresh()')
            else:
                notify(msg='删除失败,错误信息:'+six.ensure_text(data['error']))
                return
        except:
            notify(msg='删除失败')
            return

@plugin.route('/mark/<fid>/<mark>')
def mark(fid,mark):
    data = parse.urlencode(encode_obj({'fid': fid,'is_mark':mark}))
    try:
        data=xl.urlopen('http://web.api.115.com/files/edit',data=data)
        data= data.replace('\n','').replace('\r','')
        data=json.loads(data[data.index('{'):])
        if data['state']:
            xbmc.executebuiltin('Container.Refresh()')
        else:
            notify(msg='星标失败,错误信息:'+six.ensure_text(data['error']))
            return
    except:
            notify(msg='星标失败')
            return


@plugin.route('/rename/<fid>/<filename>')
def rename(fid,filename):
    newname = keyboard(text=filename)
    if not newname:
        return
    if newname==filename:
        return
    result = xl.rename(fid,newname)    
    if result:
        xbmc.executebuiltin('Container.Refresh()')
    else:
        notify(msg='重命名失败')
        
@plugin.route('/settag/<fid>/<fllist>')
def settag(fid,fllist):
    taglist=gettaglist(color=False)
    tagnamelist=[q[0] for q in taglist]
    tagidlist=[q[1] for q in taglist]
    presel=[]
    fllist=fllist.split(',')
    for fl in fllist:
        try:
            presel.append(tagidlist.index(fl))
        except:
            pass
    dialog=xbmcgui.Dialog()
    seltags=''
    sel=dialog.multiselect('设置标签',tagnamelist,preselect=presel)
    if sel:
        for tag in sel:
            try:
                seltags=seltags+tagidlist[tag]+','
            except:
                pass
    result = xl.settag(fid,seltags)    
    if result:
        xbmc.executebuiltin('Container.Refresh()')
    else:
        notify(msg='重命名失败')

def getdirinfo(cid):
    pageitems = {'0': 25,'1': 50,'2': 100}
    pageitem=pageitems[plugin.get_setting('pageitem')]
    offset=0
    data=getfilelistdata(cid,offset,'0','0',searchstr='0',nf='1')
    dirinfo={}
    dirinfo['state']=data['state']
    
    if data['state']:
        dirinfo['path']=[]
        for item in data['path']:
            if item['cid']==0:
                dirinfo['path'].append((0,'ROOT'))
            else:
                dirinfo['path'].append((item['cid'],item['name']))
        dirinfo['subdirs']=[]
        for item in data['data']:
            dirinfo['subdirs'].append((item['cid'],item['n']))
        offset+=pageitem
        while data['count']>offset:
            data=getfilelistdata(cid,offset,'0','0',searchstr='0',nf='1')
            offset+=pageitem
            if data['state']:
                for item in data['data']:
                    dirinfo['subdirs'].append((item['cid'],item['n']))
            else:
                break;
    return dirinfo

def createdir(pid,cname):
    cname = keyboard(text=cname)
    if not cname:
        return pid
    data = parse.urlencode(encode_obj({'pid': pid,'cname':cname}))
    try:
        data=xl.urlopen('http://web.api.115.com/files/add',data=data)
        data= data.replace('\n','').replace('\r','')
        data=json.loads(data[data.index('{'):])
        if data['state']:
            return data['cid']
        else:
            notify(msg='新建文件夹失败,错误信息:'+six.ensure_text(data['error']))
            return pid
    except:
            notify(msg='新建文件夹失败')
            return pid

def getdir(cid,title):
    sel=-1;
    dialog = xbmcgui.Dialog()
    while True:
        dirinfo=getdirinfo(cid)
        if dirinfo['state']:
            selectlist=[]
            
            #dirname=''
            for item in dirinfo['path']:
                #dirname+=item[1]+'\\'
                if item[0]!=cid:
                    selectlist.append((item[0],colorize_label('返回到【'+item[1]+'】',color='0044FF')))
                else:
                    #if len(dirname)>30:
                    #    dirname='..'+dirname[-28:]
                    selectlist.append((item[0],colorize_label('移动到【'+item[1]+'】',color='00FF44')))
            for item in dirinfo['subdirs']:
                selectlist.append((item[0],item[1]))
            selectlist.append((-2,colorize_label('新建文件夹',color='CCCC00')))
            sel = dialog.select('源目标：'+title, [q[1] for q in selectlist])
            if sel==-1: return -1
            if cid == selectlist[sel][0]:
                return selectlist[sel][0]
            else:
                if selectlist[sel][0]==-2:
                    cid = createdir(cid,title)
                else:
                    cid = selectlist[sel][0]
        else:
            cid=0

@plugin.route('/move/<fid>/<filename>')
def move(fid,filename):
    if not 'movepid' in ids.raw_dict():
        ids['movepid']=0
    if int(ids['movepid'])<0:
        ids['movepid']=0
    
    pid=getdir(ids['movepid'],filename)
    if str(pid)!='-1':
        data = parse.urlencode(encode_obj({'fid': fid,'pid':pid}))
        try:
            data=xl.urlopen('http://web.api.115.com/files/move',data=data)
            data= data.replace('\n','').replace('\r','')
            data=json.loads(data[data.index('{'):])
            if data['state']:
                xbmc.executebuiltin('Container.Refresh()')
            else:
                notify(msg='移动失败,错误信息:'+six.ensure_text(data['error']))
                return
        except:
                notify(msg='移动失败')
                return
        ids['movepid']=pid

def getfilelistdata(cid,offset,star,typefilter='0',searchstr='0',nf='0'):
    sorttype ='user_ptime'
    if cursorttype['s']=='2' or cursorttype['s']=='3':
        sorttype ='file_size'
    if cursorttype['s']=='4' or cursorttype['s']=='5':
        sorttype ='file_name'
    sortasc='0'
    if cursorttype['s']=='1' or cursorttype['s']=='2' or cursorttype['s']=='4':
        sortasc='1'
    #notify('%s  %s'%(sorttype,sortasc))
    pageitems = {'0': '25','1': '50','2': '100'}
    pageitem=pageitems[plugin.get_setting('pageitem')]
    return xl.getfilelist(cid,offset,pageitem,star,sorttype,sortasc,typefilter,nf=nf,search_value=searchstr)
    
@plugin.route('/getfilelist/<cid>/<offset>/<star>/<typefilter>/<searchstr>/<changesort>')
def getfilelist(cid,offset,star,typefilter='0',searchstr='0',changesort='0'):
    comm.subcache.clear()
    sorttypelist=['从新到旧','从旧到新','从小到大','从大到小','从A到Z','从Z到A']
    if changesort=='1':
        dialog = xbmcgui.Dialog()
        cursorttype['s']=str(dialog.select('文件排序',sorttypelist))
        if cursorttype['s']=='-1':
            return None
    
    typefilter=str(typefilter)
    if typefilter=='-1':
        dialog = xbmcgui.Dialog()
        typefilter=dialog.select('类型筛选',['全部','视频','图片','音乐'])
        typefilter=str(typefilter)
        if typefilter=='-1':
            return None
        if typefilter=='1': typefilter='4'
    
    data=getfilelistdata(cid,offset,star,typefilter,searchstr)
    #plugin.log.error(str(data))
    if data['state']:

        #playlistvideo = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        #playlistvideo.clear()
        
        imagecount=0
        items=[]
        
        itemname='root'
        milkname='115'
        if cid!='0':
            items.append({'label': colorize_label('返回到【%s】'%colorize_label('root', 'dir'),'back'), 'path': plugin.url_for('getfilelist',cid=0,    offset=0,star='0',typefilter=0,searchstr='0',changesort='0')})
        if 'path' in data:
            for item in data['path']:
                if item['cid']!=0 and item['cid']!=cid:
                    items.append({'label': colorize_label('返回到【%s】'%colorize_label(item['name'], 'dir'),'back'), 'path': plugin.url_for('getfilelist',cid=item['cid'],offset=0,star='0',typefilter=0,searchstr='0',changesort='0')})
                elif item['cid']==cid:
                    itemname=item['name']
                    milkname=itemname
        if 'folder' in data:
            #if 'pid' in data['folder']:
            #    items.append({'label': colorize_label('返回到【%s】'%colorize_label(data['folder']['pid'], 'dir'),'back'), 'path': plugin.url_for('getfilelist',cid=data['folder']['pid'],offset=0,star='0',typefilter=0,searchstr='0',changesort='0')})
            if 'name' in data['folder']:
                itemname=data['folder']['name']
                milkname=itemname
        if searchstr!='' and searchstr!='0':
            milkname=milkname+'_'+searchstr
        if star=='1':
            milkname=milkname+'_star'
        milkname=milkname[-20:].replace('\n','').replace('\r','')
        if str(plugin.get_setting('genm3u8'))=='true':
            items.append({'label': '生成M3U8文件', 'path': plugin.url_for('m3u8',cid=cid,offset=offset,star=star,typefilter=typefilter,searchstr=searchstr,name=milkname)})
        
        #notify('{"cid":"%s"}'%(cid))
        if searchstr=='' or searchstr=='0':
            items.append({'label': '搜索当前目录【%s】'%colorize_label(itemname, 'dir'),
                        'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'disksearch.png') ), 
                        'path': plugin.url_for('searchinit',stypes='pan',sstr='0',modify='0',otherargs='{"cid":"%s"}'%(cid))})
            stardisp=colorize_label('★星标过滤-'+('已启用' if star=='1' else '已禁用'), 'star'+str(star))
            items.append({'label': stardisp,'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'star.png') ), 'path': plugin.url_for('getfilelist',cid=cid,offset=0,star='1' if star=='0' else '0',typefilter=typefilter,searchstr=searchstr,changesort='0')})
        else:
            items.append({'label': '返回当前目录【%s】'%colorize_label(itemname, 'dir'),
                        'path': plugin.url_for('getfilelist',cid=cid,offset=0,star='0',typefilter=typefilter,searchstr='0',changesort='0')})
        if 'order' in data:
            sorttypedisp=colorize_label('文件排序:'+sorttypelist[int(cursorttype['s'])], 'sort')
            items.append({'label': sorttypedisp, 'path': plugin.url_for('getfilelist',cid=cid,offset=0,star=star,typefilter=typefilter,searchstr=six.ensure_binary(searchstr),changesort='1')})
        typedisp=colorize_label('筛选:全部', 'filter')
        if typefilter=='4':typedisp=colorize_label('筛选:视频', 'filter')
        if typefilter=='2':typedisp=colorize_label('筛选:图片', 'filter')
        if typefilter=='3':typedisp=colorize_label('筛选:音乐', 'filter')
        items.append({'label': typedisp, 'path': plugin.url_for('getfilelist',cid=cid,offset=0,
        star=star,typefilter='-1',searchstr=six.ensure_binary(searchstr),changesort='0')})
        if 'data' in data:
            for item in data['data']:
                #data['data']有时不是list,而是dict, foreach后返回的是key文本。20180425
                if not isinstance(item, dict):
                    item=data['data'][item]
                listitem=getListItem(item,itemname)
                if listitem:
                    items.append(listitem)
                    if 'ms' in item:
                        imagecount+=1
        pageitems = {'0': '25','1': '50','2': '100'}
        pageitem=pageitems[plugin.get_setting('pageitem')]
        if data['count']>int(offset)+int(pageitem):
            items.append({'label': colorize_label('下一页', 'next'),
                'path': plugin.url_for('getfilelist',cid=cid,offset=str(int(offset)+int(pageitem)),
                                        star=star,typefilter=typefilter,searchstr=six.ensure_binary(searchstr),changesort='0'),
                'thumbnail':xbmc.translatePath( os.path.join( IMAGES_PATH, 'nextpage.png') )})
        #plugin.set_content('movies')
        if imagecount >= 10 and imagecount * 2 > len(items):
            #plugin.set_content('images')
            comm.setthumbnail=True
        #notify(str(comm.subcache.raw_dict()))
        return items
    else:
        notify(msg='数据获取失败,错误信息:'+six.ensure_text(data['error']))
        login()
        return

def getimgurl(pc):
    data=xl.urlopen('http://web.api.115.com/files/image?pickcode='+pc+'&_='+str(int(time.time())))        
    data=json.loads(data[data.index('{'):])
    imageurl=''
    if data['state']:
        imageurl=data['data']['source_url']
    return imageurl

@plugin.route('/playimg/<pc>/<name>')
def playimg(pc,name):
    imgurl=xl.getfiledownloadurl(pc,changeserver='',withcookie=True)
    xbmc.executebuiltin("ShowPicture(%s)" % (imgurl))
    return
    
def getstm(data,iso,stm):
    if iso=='1':
        return '99'
    
    if stm=='7':
        return '99'
    if stm=='6':
        return '15000000'
    if stm=='5':
        return '7500000'
    if stm=='4':
        return '3000000'
    if stm=='3':
        return '1800000'
    if stm=='2':
        return '1200000'
    if stm=='1':
        return '800000'
    
    if stm=='0' or stm=='-99':
        qtyps=[]
        if data['state']:
            if 'definition_list' in data:
                if '800000' in data['definition_list']:
                    qtyps.append(('标清','800000'))
                if '1200000' in data['definition_list']:
                    qtyps.append(('高清','1200000'))
                if '1800000' in data['definition_list']:
                    qtyps.append(('超清','1800000'))
                if '3000000' in data['definition_list']:
                    qtyps.append(('1080p','3000000'))
                if '7500000' in data['definition_list']:
                    qtyps.append(('4K','7500000'))
                if '15000000' in data['definition_list']:
                    qtyps.append(('原画','15000000'))
        if len(qtyps)<=0:
            if stm=='-99':
                return '-1'
            else:
                return '99'
        dialog = xbmcgui.Dialog()
        if stm=='0':
            qtyps.append(( colorize_label('原码','star1'),'99'))
        sel = dialog.select('清晰度', [q[0] for q in qtyps])
        if sel==-1: return '-1'
        stm=str(qtyps[sel][1])
    return stm

def getchangeserver():
    #modify 2018-04-04
    #return 'cdnfhnfile.115.com'
    return '0'
    dialog = xbmcgui.Dialog()
    changeserver=''
    servers = [['cdntel.115.com','vipcdntel.115.com','mzvipcdntel.115.com','fscdntel.115.com','mzcdntel.115.com'],
                ['cdnuni.115.com','vipcdnuni.115.com','mzvipcdnuni.115.com','fscdnuni.115.com','mzcdnuni.115.com'],
                ['cdngwbn.115.com','vipcdngwbn.115.com','mzvipcdngwbn.115.com','mzcdngwbn.115.com','cdnogwbn.115.com'],
                ['cdnctt.115.com','vipcdnctt.115.com','mzvipcdnctt.115.com']]
    
    
    serverchange=int(plugin.get_setting('serverchange'))
    if serverchange>=1 and serverchange<=5:
        selectservers=[]
        if serverchange==1:
            selectservers=sum(servers,[])
        else:
            selectservers=servers[serverchange-2]
        selectservers.insert(0,'不替换')
        sel = dialog.select('CDN替换',selectservers)
        if sel<0:changeserver='-1'
        if sel>0:changeserver=selectservers[sel]
    if serverchange>=6:
        selectservers=sum(servers,[])
        changeserver = selectservers[serverchange-6]
    return changeserver
    
def getvideourl(pc,fid,stm,name=''):
    videourl=''
    if stm=='99':
        changeserver=getchangeserver()
        if changeserver=='-1':
            return '-1'
        #if changeserver!='':
        #    notify('CDN服务器:'+changeserver)
        playmode=str(plugin.get_setting('playmode'))
        videourl=xl.getfiledownloadurl(pc,changeserver=changeserver,withcookie=True)
        match = re.search("//(?P<CDN>.*115\x2ecom)/", videourl, re.IGNORECASE | re.DOTALL)
        if match:
            #pass
            notify('CDN服务器:'+ match.group("CDN"))
        if playmode=='0' and videourl:
            #preurl=pre_file_play(fid)
            #result=_http(preurl)
            videourl=get_file_download_url(pc,fid,isvideo=True,changeserver=changeserver,name=parse.quote_plus(name))
            #notify('Name:'+ name)
            #videourl=get_file_download_url(pc,fid,isvideo=True,changeserver='cdamz.115.com',name=name)
        #videourl=videourl+'|User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
    else:
        datam=xl.urlopen('http://115.com/api/video/m3u8/'+pc+'.m3u8')
        m3u8urls=[]
        for match in re.finditer("BANDWIDTH=(?P<bandwidth>.*?)\x2C.*?(?P<url>http.*?)\r", datam, re.IGNORECASE | re.DOTALL):
            m3u8urls.append((int(match.group('bandwidth')),match.group('url')))
        m3u8urls.sort(key=lambda x:x[0],reverse=True)
        for url in m3u8urls:
            if url[0]<=int(stm):
                videourl= url[1]
                break
    return videourl

def getfiledata(pc):
    data=xl.urlopen('http://web.api.115.com/files/video?pickcode='+pc+'&_='+str(int(time.time())))
    data= data.replace('\n','').replace('\r','')
    data=json.loads(data[data.index('{'):])
    if not data['state']:
        data=xl.urlopen('https://webapi.115.com/files/download?pickcode='+pc+'&_='+str(int(time.time())))
        data= data.replace('\n','').replace('\r','')
        data=json.loads(data[data.index('{'):])
    return data
    
@plugin.route('/play/<pc>/<name>/<iso>')
def play(pc,name,iso):
    data=getfiledata(pc)
    stm=str(plugin.get_setting('resolution'))
    stm=getstm(data,iso,stm)
    if stm=='-1':
        return
    videourl=''
    if int(stm)>0:
        videourl=getvideourl(pc,data['file_id'],stm,name)
    if videourl=='':
        notify(msg='无视频文件.')
        return
    if videourl=='-1':
        return
        
    sub_pcs={}
    if data['state']:
        if 'subtitle_info' in data and str(stm)!='99':
            for s in data['subtitle_info']:
                sub_pcs[('_builtin_'+s['title'])]=s['url']
    subpath=''
    name=six.ensure_text(name)
    #notify(msg=str(type(name)))
    name=name[:name.rfind('.')].lower()
    #notify(msg=str(comm.subcache.raw_dict()))
    for k,v in comm.subcache.items():
        if k.lower().find(name)!= -1:
            #notify(k)
            #sub_pcs['_same_'+k]=get_file_download_url(v,'')
            if k[k.rfind('.'):]=='.idx_sub':
                if 'idx' in v and 'sub' in v:
                    urlidx=xl.getfiledownloadurl(v['idx'],changeserver='',withcookie=True)
                    urlsub=xl.getfiledownloadurl(v['sub'],changeserver='',withcookie=True)
                    sub_pcs['_same_'+k]=urlidx+ ' ' +urlsub
            else:
                sub_pcs['_same_'+k]=xl.getfiledownloadurl(v,changeserver='',withcookie=True)
    
    if plugin.get_setting('subtitle')=='true':
        try:
            uid = xl.getcookieatt('UID')
            uid = uid[:uid.index('_')]
            data=xl.urlopen('http://web.api.115.com/movies/subtitle?pickcode='+pc)
            data=json.loads(data[data.index('{'):])
            if data['state']:
                for s in data['data']:
                    sub_pcs[(s['language']+'_'+s['filename'])]=s['url']
        except:
            pass
                
    if len(sub_pcs)==1:
        subpath = os.path.join( __subpath__,list(sub_pcs.keys())[0])
        suburl=sub_pcs[list(sub_pcs.keys())[0]]
        notify('加载了1个字幕')
        
    elif len(sub_pcs)>1:
        dialog = xbmcgui.Dialog()
        sel = dialog.select('字幕选择', [subname for subname in list(sub_pcs.keys())])
        if sel>-1: 
            subpath = os.path.join( __subpath__,list(sub_pcs.keys())[sel])
            suburl = sub_pcs[list(sub_pcs.keys())[sel]]
    
    if subpath!='' and suburl!='':
        if subpath[subpath.rfind('.'):]=='.idx_sub':
            subpath=subpath[:subpath.rfind('.')]
            [urlidx,urlsub]=suburl.split(' ')
            subdata = xl.urlopen(urlidx,binary=True)
            with open(six.ensure_binary(subpath+'.idx'), "wb") as subFile:
                subFile.write(subdata)
            subFile.close()
            subdata = xl.urlopen(urlsub,binary=True)
            with open(six.ensure_binary(subpath+'.sub'), "wb") as subFile:
                subFile.write(subdata)
            subFile.close()
            subpath=subpath+'.idx'
        else:
            subdata = xl.urlopen(suburl,binary=True)
            with open(six.ensure_binary(subpath), "wb") as subFile:
                subFile.write(subdata)
            subFile.close()

    #plugin.set_resolved_url(videourl,six.ensure_text(subpath))
    plugin.set_resolved_url(videourl)
    
    if subpath:
        player = xbmc.Player()
        for _ in range(30):
            if player.isPlaying():
                break
            time.sleep(1)
        if six.PY2:
            player.setSubtitles(six.ensure_binary(subpath))
        else:
            player.setSubtitles(six.ensure_text(subpath))


@plugin.route('/ffmpeg/<pc>/<name>')
def ffmpeg(pc,name):
    data=getfiledata(pc)
    stm=getstm(data,'0','0')
    videourl=''
    if int(stm)>0:
        videourl=getvideourl(pc,data['file_id'],stm,name)
    if videourl=='':
        notify(msg='无视频文件.')
        return
    if videourl=='-1':
        return
    plugin.log.error(videourl)
    ext='.mp4'
    name=six.ensure_text(name)
    #if str(stm)=='99':
        #ext=name[name.rfind('.'):].lower()
    name=name[:name.rfind('.')].lower()
    
    sub_pcs={}
    if data['state']:
        if 'subtitle_info' in data and str(stm)!='99':
            for s in data['subtitle_info']:
                sub_pcs[('_builtin_'+s['title'])]=s['url']
    
    for k,v in comm.subcache.items():
        if k.lower().find(name)!= -1:
            #notify(k)
            #sub_pcs['_same_'+k]=get_file_download_url(v,'')
            if k[k.rfind('.'):]=='.idx_sub':
                if 'idx' in v and 'sub' in v:
                    urlidx=xl.getfiledownloadurl(v['idx'],changeserver='',withcookie=True)
                    urlsub=xl.getfiledownloadurl(v['sub'],changeserver='',withcookie=True)
                    sub_pcs['_same_'+k]=urlidx+ ' ' +urlsub
            else:
                sub_pcs['_same_'+k]=xl.getfiledownloadurl(v,changeserver='',withcookie=True)
    
    if plugin.get_setting('subtitle')=='true':
        try:
            uid = xl.getcookieatt('UID')
            uid = uid[:uid.index('_')]
            data=xl.urlopen('http://web.api.115.com/movies/subtitle?pickcode='+pc)
            data=json.loads(data[data.index('{'):])
            if data['state']:
                for s in data['data']:
                    sub_pcs[(s['language']+'_'+s['filename'])]=s['url']
        except:
            pass
            
    ffmpegdowloadpath=xbmc.translatePath('/sdcard/Download/115/ffmpegdowload/')
    if not os.path.exists(ffmpegdowloadpath):
        os.makedirs(ffmpegdowloadpath)
    suburl=''
    subpath=''
    if len(sub_pcs)==1:
        subpath = os.path.join( ffmpegdowloadpath,list(sub_pcs.keys())[0])
        suburl=sub_pcs[list(sub_pcs.keys())[0]]
        notify('发现1个字幕')
        
    elif len(sub_pcs)>1:
        dialog = xbmcgui.Dialog()
        sel = dialog.select('字幕选择', [subname for subname in list(sub_pcs.keys())])
        if sel>-1: 
            subpath = os.path.join(ffmpegdowloadpath,list(sub_pcs.keys())[sel])
            suburl = sub_pcs[list(sub_pcs.keys())[sel]]
            
    if subpath!='' and suburl!='':
        if subpath[subpath.rfind('.'):]=='.idx_sub':
            subpath=subpath[:subpath.rfind('.')]
            [urlidx,urlsub]=suburl.split(' ')
            subdata = xl.urlopen(urlidx,binary=True)
            with open(six.ensure_binary(subpath+'.idx'), "wb") as subFile:
                subFile.write(subdata)
            subFile.close()
            subdata = xl.urlopen(urlsub,binary=True)
            with open(six.ensure_binary(subpath+'.sub'), "wb") as subFile:
                subFile.write(subdata)
            subFile.close()
            subpath=subpath+'.idx'
        else:
            subdata = xl.urlopen(suburl,binary=True)
            with open(six.ensure_binary(subpath), "wb") as subFile:
                subFile.write(subdata)
            subFile.close()
    
    outputfname=os.path.abspath(xbmc.translatePath(os.path.join(ffmpegdowloadpath, name+ext)))
    batfname=xbmc.translatePath( os.path.join(ffmpegdowloadpath, name+'.bat') )
    with open(batfname, "wb") as batFile:
        batFile.write(ffmpegdl(videourl,outputfname,subpath,stm).encode('utf-8'))
        
    batFile.close()
    notify('已在/Download/115/ffmpegdowload/目录下生成bat文件')
    #notify(batfname)
    
@plugin.route('/offline_bt/<sha1>')
def offline_bt(sha1):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('115网盘提示', '是否离线文件?')
    if ret:
        uid = xl.getcookieatt('UID')
        uid = uid[:uid.index('_')]
        data=xl.urlopen('http://115.com/?ct=offline&ac=space&_='+str(int(time.time())))
        data=json.loads(data[data.index('{'):])
        sign=data['sign']
        _time=data['time']
        data = parse.urlencode(encode_obj({'sha1': sha1,'uid':uid,'sign':sign,'time':_time}))
        data=xl.urlopen('http://115.com/web/lixian/?ct=lixian&ac=torrent',data=data)
        data=json.loads(data[data.index('{'):])
        if data['state']:
            wanted='0'
            for i in range(1,len(data['torrent_filelist_web'])):
                wanted+='%02C'
                wanted+=str(i)
            torrent_name=data['torrent_name']
            info_hash=data['info_hash']
            data = parse.urlencode(encode_obj({'info_hash': info_hash,'wanted': wanted,'savepath': torrent_name,'uid':uid,'sign':sign,'time':_time}))
            
            data=xl.urlopen('http://115.com/web/lixian/?ct=lixian&ac=add_task_bt',data=data)
            data=json.loads(data[data.index('{'):])
            if data['state']:
                notify('离线任务添加成功！', delay=2000)
            else:
                notify(data['error_msg'], delay=2000)
                if data['errcode']==911:
                    captcha()
                return
        else:
            notify(data['error_msg'], delay=2000)
            return
    else:
        return

def pre_file_play(fid):
    return 'http://%s/pre/%s/%s' % (plugin.get_setting('proxyserver'),fid,xl.getcookiesstr())
        
def get_file_download_url(pc,fid,isvideo=False,changeserver='',name=''):
    if isvideo:
        result='http://%s/115/%s/%s/%s/%s' % (plugin.get_setting('proxyserver'),fid,xl.getcookiesstr(),changeserver,name)
    else:
        result=xl.getfiledownloadurl(pc,changeserver,withcookie=True)
    return result

@plugin.route('/delete_offline_list/<hashinfo>/<warringmsg>')
def delete_offline_list(hashinfo,warringmsg):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('离线任务删除', warringmsg)
    if ret:
        data=xl.urlopen("http://115.com/web/lixian/?ct=lixian&ac=task_del",data=hashinfo)
        data=json.loads(data[data.index('{'):])
        
        if data['state']:
            xbmc.executebuiltin('Container.Refresh()')
        else:
            notify(msg='删除失败,错误信息:'+six.ensure_text(data['error']))
            return

@plugin.route('/offline_list')
def offline_list():
    msg_st={'-1': '任务失败','0': '任务停止','1': '下载中','2': '下载完成'}
    task=xl.offline_list()
    uid = xl.getcookieatt('UID')
    uid = uid[:uid.index('_')]
    items=[]
    clearcomplete={'time':str(int(time.time())),'uid':uid}
    clearfaile={'time':str(int(time.time())),'uid':uid}
    i=0
    j=0
    
    for item in task:
        if item['status']==2 and item['move']==1:
            clearcomplete['hash['+str(i)+']']=item['info_hash']
            i+=1
        if item['status']==-1:
            clearfaile['hash['+str(j)+']']=item['info_hash']
            j+=1
        
        listitem=ListItem(label=item['name']+colorize_label("["+msg_st[str(item['status'])]+"]", str(item['status'])), label2=None, icon=None, thumbnail=None, path=plugin.url_for('getfilelist',cid=item['file_id'],offset='0',star='0',typefilter='0',searchstr='0',changesort='0'))
        _hash = parse.urlencode(encode_obj({'uid':uid,'time':str(int(time.time())),r'hash[0]': item['info_hash']}))
        listitem.add_context_menu_items([('删除离线任务', 'RunPlugin('+plugin.url_for('delete_offline_list',hashinfo=_hash,warringmsg=six.ensure_binary('是否删除任务'))+')',)])
        
        items.append(listitem)
    if j>0:
        _hash = parse.urlencode(clearfaile)
        items.insert(0, {
            'label': colorize_label('清空失败任务','-1'),
            'path': plugin.url_for('delete_offline_list',hashinfo=_hash,warringmsg=six.ensure_binary('是否清空'+str(j)+'个失败任务'))})
    if i>0:
        _hash = parse.urlencode(clearcomplete)
        items.insert(0, {
            'label': colorize_label('清空完成任务','2'),
            'path': plugin.url_for('delete_offline_list',hashinfo=_hash,warringmsg=six.ensure_binary('是否清空'+str(i)+'个完成任务'))})
    return items

@plugin.route('/shellopen/<pc>/<fname>')
def shellopen(pc,fname):
    changeserver=getchangeserver()
    if changeserver=='-1':
        return
    #url=xl.getfiledownloadurl(pc,changeserver,True)
    data=getfiledata(pc)
    url=getvideourl(pc,data['file_id'],'99',fname)
    
    if url=='':
        notify(msg='无视频文件.')
        return
    if url=='-1':
        return
    comm.shellopenurl(url,samsung=0)

@plugin.route('/m3u8/<cid>/<offset>/<star>/<typefilter>/<searchstr>/<name>')
def m3u8(cid,offset,star,typefilter='0',searchstr='0',name='0'):
    stm='0'
    qtyps=[]        
    qtyps.append(('标清','800000'))
    qtyps.append(('高清','1200000'))
    qtyps.append(('超清','1800000'))
    qtyps.append(('1080p','3000000'))
    qtyps.append(('4K','7500000'))
    qtyps.append(('原画','15000000'))
    dialog = xbmcgui.Dialog()
    sel = dialog.select('清晰度', [q[0] for q in qtyps])
    if sel==-1: return '-1'
    stm=str(qtyps[sel][1])

    global milkvrcount
    milkvrcount=0

    basepath='/sdcard/Download/115/'
    savepath=xbmc.translatePath( os.path.join( basepath, name))[0:40]
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    htmlfname=xbmc.translatePath( os.path.join(basepath, name[0:20]+'.html') )
    with open(htmlfname, "wb") as htmlFile:
        htmlFile.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8"><TITLE>%s</TITLE><h3>%s</h3>'%(name,name))
        htmlFile.write('\r\n')
    htmlFile.close()
    genm3u8(cid,offset,star,typefilter,searchstr,savepath,stm,name)
    
    notify(msg='在/Download/115/目录下生成'+str(milkvrcount)+'个M3U8文件！')
    
def ffmpegdl(input,output,subtitle='',stm='-1'):
    #ffmpegopt='-err_detect ignore_err -filter:v pad=11/10*iw:ih:(ow-iw)/2:0,stereo3d=sbsl:abl,crop=10/11*iw:ih:(iw-ow)/2:0,stereo3d=abl:sbsl -y -bsf:a aac_adtstoasc'
    ffmpegopt='-c copy -y -bsf:a aac_adtstoasc'
    if stm=='99':
        ffmpegopt='-c copy -y'
    dlcmd=''
    times1=''
    times2=''
    timedt=''
    
    dialog=xbmcgui.Dialog()
    ret = dialog.yesno('115网盘提示', '是否剪切片断?')
    
    if ret:
        times=keyboard(text='00:00:00',title='起始时间')
        if times:
            timee=keyboard(text=times,title='结束时间')
            if timee:
                times=time.strptime(times,'%H:%M:%S')
                times=timedelta(hours=times.tm_hour,minutes=times.tm_min,seconds=times.tm_sec)
                timee=time.strptime(timee,'%H:%M:%S')
                timee=timedelta(hours=timee.tm_hour,minutes=timee.tm_min,seconds=timee.tm_sec)
                tdelta=timee-times
                tdelta=tdelta.total_seconds()
                if tdelta>0:
                    timedt=' -t '+str(tdelta)+' '
                    timefs=timedelta(hours=0,minutes=0,seconds=30)
                    if times>timefs:
                        times1='-ss '+str(times-timefs)
                        times2='-ss 00:00:30'
                    else:
                        times1=''
                        times2='-ss '+str(times)
    
    subtitlecs=''
    subtitlets=''
    if subtitle!='':
        if subtitle[subtitle.rfind('.'):]=='.idx':
            subtitle=subtitle[:subtitle.rfind('.')]
            subtitle='-i "%s.idx" -i "%s.sub" '%(subtitle,subtitle)
            subtitlecs='-c:s dvd_subtitle'
        else:
            subtitle='-i "'+subtitle+'"'
            subtitlecs='-c:s mov_text'
        subtitlets=times1
    plugin.log.error(input)
    plugin.log.error(output)
    output=six.ensure_text(output)
    
    dlcmd='ffmpeg %s -i \"%s\" %s %s %s %s %s %s \"%s\"'%(times1,input,subtitlets,subtitle,ffmpegopt,subtitlecs,times2,timedt,output)
    #dlcmd= u'ffmpeg %s -i \"%s\" %s %s %s %s %s \"%s\"'%(times1,input,subtitle,ffmpegopt,subtitlecs,times2,timedt,output)
    
        
    #ffmpegopt='-err_detect ignore_err -filter:v pad=11/10*iw:ih:(ow-iw)/2:0,stereo3d=sbsl:abl,crop=10/11*iw:ih:(iw-ow)/2:0,stereo3d=abl:sbsl -y -bsf:a aac_adtstoasc'
    #dlcmd=dlcmd+'\r\n'+'ffmpeg -i "'+output+'" '+ffmpegopt+' "'+output+'.mp4"'
    return dlcmd
    
def genm3u8(cid,offset,star,typefilter,searchstr,savepath,stm,name):
    global milkvrcount
    if milkvrcount>=200:
        return
    data=getfilelistdata(cid,offset,star,typefilter,searchstr)
    if data['state']:
        pname=''
        if 'path' in data:
            pname=data['path'][len(data['path'])-1]['name'];
        if 'folder' in data:
            if 'name' in data['folder']:
                pname=data['folder']['name']
        pname=pname
        for item in data['data']:
            if 'sha' in item:
                if 'iv' in item:
                    fname=item['n']
                    fname=fname[:fname.rfind('.')]
                    if len(fname)<=20:
                        if 'dp' in item:
                            fname=fname+'_'+item['dp']
                        else:
                            fname=fname+'_'+pname
                    fname=fname[-40:]+'_'+pname
                    fname=fname[0:60]
                    fname=six.ensure_binary(fname.replace('\n','').replace('\r',''))
                    fname = re.sub('[\/:*?"<>|]','-',fname)
                    #plugin.log.error(fname)
                    url=getvideourl(item['pc'],item['fid'],stm)
                    if url!='':
                        m3u8fname=xbmc.translatePath(os.path.join(savepath, fname+'.m3u8'))
                        #notify(m3u8fname)
                        with open(m3u8fname, "wb") as m3u8File:
                            
                            m3u8File.write('#EXTM3U\r\n#EXT-X-STREAM-INF:PROGRAM-ID=1,NAME="%s"\r\n'%(fname))
                            m3u8File.write(url)
                        m3u8File.close()
                        
                        ffmpegdowloadpath=xbmc.translatePath('/sdcard/Download/115/ffmpegdowload/')
                        if not os.path.exists(ffmpegdowloadpath):
                            os.makedirs(ffmpegdowloadpath)
                        outputfname=xbmc.translatePath(os.path.join(ffmpegdowloadpath, fname+'.mp4'))
                        batfname=xbmc.translatePath( os.path.join(ffmpegdowloadpath, fname+'.bat') )
                        with open(batfname, "wb") as batFile:
                            batFile.write(ffmpegdl(url,os.path.abspath(outputfname)))
                            batFile.write('\r\n')
                        batFile.close()
                        '''
                        h5playpath=xbmc.translatePath('/sdcard/Download/115/html/')
                        if not os.path.exists(h5playpath):
                            os.makedirs(h5playpath)
                        h5playfname=xbmc.translatePath(os.path.join(h5playpath, fname+'.html'))
                        with open(h5playfname, "wb") as h5playFile:
                            h5playFile.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8"><TITLE>%s</TITLE><h3>%s</h3><DT><video width="640" height="480" autoplay="autoplay" src="%s" controls="controls" type="application/x-mpegURL">%s</video>'%(fname,fname,'../'+name+'/'+fname+'.m3u8',fname))
                        h5playFile.close()
                        '''
                        if url[-4:]=='m3u8':
                            htmlfname=xbmc.translatePath( os.path.join('/sdcard/Download/115/', name+'.html') )
                            with open(htmlfname, "ab") as htmlFile:
                                #htmlFile.write('<DT><a href="%s" type="video/mp4" >%s</a>\r\n'%(name+'/'+fname+'.m3u8',fname))
                                htmlFile.write('<DT><a href="%s" type="video/mp4" >%s</a>'%(url,fname))
                                #htmlFile.write('<DT><a href="%s" type="application/x-mpegURL" >%s</a>'%(url,fname))
                                #htmlFile.write('<DT><a href="html/%s.html" type="application/x-mpegURL" >%s</a>'%(fname,fname))
                                #htmlFile.write('\r\n')
                            htmlFile.close()
                        
                        
                    milkvrcount+=1
                    if milkvrcount>=200:
                        break
            else:
                genm3u8(item['cid'],'0','0','0','0',savepath,stm,name)

@plugin.route('/captcha/')
def captcha():
    captchadlg=CaptchaDlg()
    captchadlg.doModal()
    #qthread = threading.Thread(target=captchadlg.doModal,)
    #qthread.start()
    
@plugin.route('/offline/<url>')
def offline(url):
    xbmc.executebuiltin( "ActivateWindow(busydialog)" )
    data=xl.offline(url)
    #plugin.log.error(data)
    if data['state']:
        notify(' 添加离线成功',delay=1000)
    else:
        if data['errcode']==911:
            notify(data['error_msg'],delay=2000)
            captcha()
        else:
            magnet = ''
            match = re.search(r'\x3Abtih\x3a(?P<magnet>[0-9a-f]{40})', url, re.IGNORECASE | re.DOTALL)
            if match:
                magnet = match.group('magnet')
            if magnet:
                notify('磁力离线失败,已尝试下载种子文件，请一段时间后查看',delay=1000)
                #torrenturl='https://btdb.eu/tfiles/%s.torrent'%(magnet)
                #offline(torrenturl)
                torrenturl='http://itorrents.org/torrent/%s.torrent'%(magnet)
                offline(torrenturl)
            else:
                notify(' 添加离线失败,错误代码:'+data['error_msg'],delay=1000)
        
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    if data['state']:
        return data['info_hash']
    else:
        return

@plugin.route('/execmagnet/<url>/<title>/<msg>')
def execmagnet(url,title='',msg=''):
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('是否离线 '+six.ensure_text(title)+'?', msg)
    if ret:
        info_hash=offline(url)
        
if __name__ == '__main__':
    # Override default handler
    #comm.setthumbnail=False
    plugin.run()
    skindir=xbmc.getSkinDir()
    
    if comm.setthumbnail:
        if skindir in comm.ALL_VIEW_CODES['thumbnail']:
            thumbmode=comm.ALL_VIEW_CODES['thumbnail'][skindir]
            #notify(str(thumbmode))
            xbmc.executebuiltin('Container.SetViewMode(%d)' % thumbmode)
    else:
        if skindir in comm.ALL_VIEW_CODES['list']:
            listmode=comm.ALL_VIEW_CODES['list'][skindir]
            #notify(str(listmode))
            xbmc.executebuiltin('Container.SetViewMode(%d)' % listmode)

