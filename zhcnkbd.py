# -*- coding: utf-8 -*-
import os
import sys
import time
import httplib
import xbmc
import xbmcgui
import json
from xbmcswift2 import Plugin

reload(sys)
sys.setdefaultencoding('utf-8')

plugin = Plugin()
pgpath = plugin.addon.getAddonInfo('path')

ACTION_PARENT_DIR     = 9
ACTION_PREVIOUS_MENU  = (10, 92)
ACTION_CONTEXT_MENU   = 117

CTRL_ID_BACK = 8
CTRL_ID_SPACE = 32
CTRL_ID_RETN = 300
CTRL_ID_LANG = 302
CTRL_ID_CAPS = 303
CTRL_ID_SYMB = 304
CTRL_ID_LEFT = 305
CTRL_ID_RIGHT = 306
CTRL_ID_IP = 307
CTRL_ID_TEXT = 310
CTRL_ID_HEAD = 311
CTRL_ID_CODE = 401
CTRL_ID_HZLIST = 402

class InputWindow(xbmcgui.WindowXMLDialog):
	def __init__( self, *args, **kwargs ):
		self.totalpage = 0
		self.nowpage = 0
		self.words = ''
		self.py = ''
		self.bg = 0
		self.ed = 20
		self.wordpgs = []   #word page metadata
		self.inputString = kwargs.get("default") or ""
		self.heading = kwargs.get("heading") or ""
		self.conn = httplib.HTTPConnection('olime.baidu.com')
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) {0}{1}'.format(
				'AppleWebKit/537.36 (KHTML, like Gecko) ',
				'Chrome/28.0.1500.71 Safari/537.36'),
		}
		xbmcgui.WindowXMLDialog.__init__(self)

	def onInit(self):
		self.setKeyToChinese()
		self.getControl(CTRL_ID_HEAD).setLabel(self.heading)
		self.getControl(CTRL_ID_CODE).setLabel('')
		self.getControl(CTRL_ID_TEXT).setLabel(self.inputString)
		self.confirmed = False

	def onFocus( self, controlId ):
		self.controlId = controlId

	def onClick( self, controlID ):
		if controlID == CTRL_ID_CAPS:#big
			self.getControl(CTRL_ID_SYMB).setSelected(False)
			if self.getControl(CTRL_ID_CAPS).isSelected():
				self.getControl(CTRL_ID_LANG).setSelected(False)
			self.setKeyToChinese()
		elif controlID == CTRL_ID_IP:#ip
			dialog = xbmcgui.Dialog()
			value = dialog.numeric( 3, __language__(2), '' )
			self.getControl(CTRL_ID_TEXT).setLabel(
				self.getControl(CTRL_ID_TEXT).getLabel()+value)
		elif controlID == CTRL_ID_SYMB:#num
			self.setKeyToChinese()
		elif controlID == CTRL_ID_LANG:#en/ch
			if self.getControl(CTRL_ID_LANG).isSelected():
				self.getControl(CTRL_ID_CAPS).setSelected(False)
			self.setKeyToChinese()
		elif controlID == CTRL_ID_BACK:#back
			if self.getControl(CTRL_ID_LANG).isSelected() and \
			   len(self.getControl(CTRL_ID_CODE).getLabel())>0:
				self.getControl(CTRL_ID_CODE).setLabel(
					self.getControl(CTRL_ID_CODE).getLabel()[0:-1])
				self.getChineseWord(self.getControl(CTRL_ID_CODE).getLabel())
			else:
				self.getControl(CTRL_ID_TEXT).setLabel(
					self.getControl(CTRL_ID_TEXT).getLabel().
					decode("utf-8")[0:-1])
		elif controlID == CTRL_ID_RETN:#enter
			newText = self.getControl(CTRL_ID_TEXT).getLabel()
			if not newText: return
			self.inputString = newText
			self.confirmed = True
			self.close()
		elif controlID == CTRL_ID_LEFT:#left
			if self.nowpage>0:
				self.nowpage -=1
			self.changepages()
		elif controlID == CTRL_ID_RIGHT:#right
			self.nowpage +=1
			self.changepages()
		elif controlID == CTRL_ID_SPACE:#space
			self.getControl(CTRL_ID_TEXT).setLabel(
				self.getControl(CTRL_ID_TEXT).getLabel() + ' ')
		else:
			if self.getControl(CTRL_ID_LANG).isSelected() and \
			   not self.getControl(CTRL_ID_SYMB).isSelected():
				if controlID>=65 and controlID<=90:
					s = self.getControl(CTRL_ID_CODE).getLabel() + \
						self.getControl(controlID).getLabel().lower()
					self.getControl(CTRL_ID_CODE).setLabel(s)
					self.getChineseWord(s)
				elif controlID>=48 and controlID<=57:#0-9
					#i = self.nowpage*(self.wordperpage+1)+(controlID-48)
					i = self.wordpgs[self.nowpage][0] + (controlID - 48)
					hanzi = self.words[i]
					self.getControl(CTRL_ID_TEXT).setLabel(
						self.getControl(CTRL_ID_TEXT).getLabel()+ hanzi)
					self.getControl(CTRL_ID_CODE).setLabel('')
					#Comment out to allow user to reselect the last hzlist
					#self.getControl(CTRL_ID_HZLIST).setLabel('')
					#self.words = []
			else:
				self.getControl(CTRL_ID_TEXT).setLabel('%s%s' % (
					self.getControl(CTRL_ID_TEXT).getLabel(),
					self.getControl(controlID).getLabel().encode('utf-8')))

	def onAction(self,action):
		keycode = action.getButtonCode()

		# xbmc remote keyboard control handler
		if keycode >= 61728 and keycode <= 61823:
			keychar = chr(keycode - 61728 + ord(' '))
			if keychar >='0' and keychar <= '9':
				self.onClick(ord(keychar))
			elif self.getControl(CTRL_ID_LANG).isSelected():
				s = self.getControl(CTRL_ID_CODE).getLabel() + keychar
				self.getControl(CTRL_ID_CODE).setLabel(s)
				self.getChineseWord(s)
			else:
				self.getControl(CTRL_ID_TEXT).setLabel(
					self.getControl(CTRL_ID_TEXT).getLabel()+keychar)
		elif keycode == 61706:
			self.onClick(CTRL_ID_RETN)

		# Hard keyboard handler
		elif keycode >= 61505 and keycode <= 61530: #a-z
			if self.getControl(CTRL_ID_LANG).isSelected():
				keychar = chr(keycode - 61505 + ord('a'))
				s = self.getControl(CTRL_ID_CODE).getLabel() + keychar
				self.getControl(CTRL_ID_CODE).setLabel(s)
				self.getChineseWord(s)
			else:
				if self.getControl(CTRL_ID_CAPS).isSelected():
					keychar = chr(keycode - 61505 + ord('A')) #A-Z
				else:
					keychar = chr(keycode - 61505 + ord('a'))
				self.getControl(CTRL_ID_TEXT).setLabel(
					self.getControl(CTRL_ID_TEXT).getLabel()+keychar)

		#0-9(Eden)-no overlapping code with Dharma
		elif keycode >= 61488 and keycode <= 61497:
			self.onClick( keycode-61488+48 )
		#0-9(Dharma)-no overlapping code with Eden
		elif keycode >= 61536 and keycode <= 61545:
			self.onClick( keycode-61536+48 )
		#Eden & Dharma scancode difference
		elif keycode == 61500 or keycode == 192700:
			self.onClick( CTRL_ID_LEFT ) # <
		#Eden & Dharma scancode difference
		elif keycode == 61502 or keycode == 192702:
			self.onClick( CTRL_ID_RIGHT ) # >
		elif keycode == 61472:
			self.onClick( CTRL_ID_SPACE )
		elif keycode == 61448:
			self.onClick( CTRL_ID_BACK )
		elif action.getId() in ACTION_PREVIOUS_MENU:
			self.close()

	def changepages (self):
		self.getControl(CTRL_ID_HZLIST).setLabel('')
		hzlist = ''
		if not self.wordpgs: return
		if self.nowpage >= self.totalpage-1:
			self.bg += 20
			self.ed += 20
			self.getChineseWord(self.py, self.bg, self.ed)
			return
		curwpg = self.wordpgs[self.nowpage]
		for i, w in enumerate(self.words[curwpg[0]:curwpg[1]]):
			hzlist = hzlist + str(i) + '.' + w +' '
		if self.nowpage > 0:
			hzlist = '<' + hzlist
		if self.nowpage < self.totalpage-1:
			hzlist = hzlist + '>'
		self.getControl(CTRL_ID_HZLIST).setLabel(hzlist)

	def getChineseWord (self, py, bg=0, ed=20):
		self.getControl(CTRL_ID_HZLIST).setLabel('')
		#if HANZI_MB.has_key(py):
		if py=='': return
		if not bg:
			self.nowpage = 0
			self.totalpage = 0
			self.wordpgs = []
			self.words= []
			self.py = py
			self.bg = 0
			self.ed = 20
		wres = self.getwords(py, bg, ed)
		if wres:
			self.words.extend(wres)
			self.wordpgs = []
			inum = 0
			for s, w in enumerate(self.words):
				if len(''.join(self.words[inum:s+1]).decode('utf-8')) + (
						s+1-inum)*2 >30:
					self.wordpgs.append((inum, s))
					inum = s
			if len(self.words) > inum:
				self.wordpgs.append((inum, len(self.words)))
			self.totalpage = len(self.wordpgs)
		else:
			self.nowpage = self.totalpage - 1

		hzlist = ''
		curwpg = self.wordpgs[self.nowpage]
		for i, w in enumerate(self.words[curwpg[0]:curwpg[1]]):
			hzlist = hzlist + str(i) + '.' + w +' '
		if self.nowpage > 0:
			hzlist = '<' + hzlist
		if self.nowpage < self.totalpage-1:
			hzlist = hzlist + '>'
		self.getControl(CTRL_ID_HZLIST).setLabel(hzlist)

	def getwords(self, py, bg, ed):
		t = time.time()
		
		urlsuf = '/py?input={0}&inputtype=py&bg={1}&ed={2}&{3}&result=hanzi&resultcoding=unicode&ch_en=0&clientinfo=web&version=1'.format(
			py, bg, ed,
			'result=hanzi&resultcoding=unicode&ch_en=0&clientinfo=web')
		try:
			self.conn.request('GET', urlsuf, headers=self.headers)
		except Exception as e:
			self.conn = httplib.HTTPConnection('olime.baidu.com')
			self.conn.request('GET', urlsuf, headers=self.headers)
		rsp = self.conn.getresponse()
		
		cookie = rsp.getheader('Set-Cookie', '')
		if 'Cookie' not in self.headers and cookie:
			self.headers['Cookie'] = cookie
		httpdata = rsp.read()

		words = []
		try:
			jsondata = json.loads(httpdata)
			
		except ValueError:
			return None
		
		#plugin.log.error(jsondata)
		for word in jsondata['result'][0]:
			words.append(word[0].encode('utf-8'))
		#print match, words
		return words

	def setKeyToChinese (self):
		self.getControl(CTRL_ID_CODE).setLabel('')
		if self.getControl(CTRL_ID_SYMB).isSelected():
			i = 48
			for c in ')!@#$%^&*(':
				self.getControl(i).setLabel(c)
				i+=1
				if i > 57: break
			i = 65
			for c in '[]{}-_=+;:\'",.<>/?\\|`~':
				self.getControl(i).setLabel(c)
				i+=1
				if i > 90: break
			for j in range(i,90+1):
				self.getControl(j).setLabel('')
		else:
			for i in range(48, 57+1):
				keychar = chr(i - 48 + ord('0'))
				self.getControl(i).setLabel(keychar)
			if self.getControl(CTRL_ID_CAPS).isSelected():
				for i in range(65, 90+1):
					keychar = chr(i - 65 + ord('A'))
					self.getControl(i).setLabel(keychar)
			else:
				for i in range(65, 90+1):
					keychar = chr(i - 65 + ord('a'))
					self.getControl(i).setLabel(keychar)
		if self.getControl(CTRL_ID_LANG).isSelected():
			self.getControl(400).setVisible(True)
			self.nowpage = 0
			self.changepages()
		else:
			self.getControl(400).setVisible(False)

	def isConfirmed(self):
		return self.confirmed

	def getText(self):
		return self.inputString


class Keyboard:
	def __init__( self, default='', heading='' ):
		self.confirmed = False
		self.inputString = default
		self.heading = heading

	def doModal (self):
		self.win = InputWindow(
			"DialogKeyboardChinese.xml", pgpath, defaultSkin='Default',
			heading=self.heading, default=self.inputString)
		self.win.doModal()
		self.confirmed = self.win.isConfirmed()
		self.inputString = self.win.getText()
		del self.win

	def setHeading(self, heading):
		self.heading = heading

	def isConfirmed(self):
		return self.confirmed

	def getText(self):
		return self.inputString
