# -*- coding: utf-8 -*-
#VERSION: 1.41

# Author:
#  Fabien Devaux <fab AT gnux DOT info>
# Contributors:
#  Christophe Dumez <chris@qbittorrent.org> (qbittorrent integration)
#  Thanks to gab #gcu @ irc.freenode.net (multipage support on PirateBay)
#  Thanks to Elias <gekko04@users.sourceforge.net> (torrentreactor and isohunt search engines)
#
# Licence: BSD

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the author nor the names of its contributors may be
#      used to endorse or promote products derived from this software without
#      specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import urllib,re,threading,Queue,xbmc

from os import path
from glob import glob
from sys import argv
from fix_encoding import fix_encoding

################################################################################
# Every engine should have a "search" method taking
# a space-free string as parameter (ex. "family+guy")
# it should call prettyPrinter() with a dict as parameter.
# The keys in the dict must be: link,name,size,seeds,leech,engine_url
# As a convention, try to list results by decrasing number of seeds or similar
################################################################################
from xbmcswift2 import Plugin
plugin = Plugin()
def initialize_engines():
	""" Import available engines

		Return list of available engines
	"""
	supported_engines = []

	engines = glob(path.join(path.dirname(__file__), 'engines', '*.py'))
	for engine in engines:
		engi = path.basename(engine).split('.')[0].strip()
		
		if len(engi) == 0 or engi.startswith('_'):
			continue
		supported_engines.append(engi)
		

	return supported_engines

def engines_to_xml(supported_engines):
	""" Generates xml for supported engines """
	tab = " " * 4

	for short_name in supported_engines:
		search_engine = globals()[short_name]()

		supported_categories = ""
		if hasattr(search_engine, "supported_categories"):
			supported_categories = " ".join((key for key in search_engine.supported_categories.keys()
											 if key is not "all"))

		yield  "".join((tab, "<", short_name, ">\n",
						tab, tab, "<name>", search_engine.name, "</name>\n",
						tab, tab, "<url>", search_engine.url, "</url>\n",
						tab, tab, "<categories>", supported_categories, "</categories>\n",
						tab, "</", short_name, ">\n"))

def displayCapabilities(supported_engines):
	"""
	Display capabilities in XML format
	<capabilities>
	  <engine_short_name>
		<name>long name</name>
		<url>http://example.com</url>
		<categories>movies music games</categories>
	  </engine_short_name>
	</capabilities>
	"""
	xml = "".join(("<capabilities>\n",
				   "".join(engines_to_xml(supported_engines)),
				   "</capabilities>"))
	print(xml)

class workerSearch(threading.Thread):
	def __init__(self,queue,queueResult):
		threading.Thread.__init__(self)
		self.queue=queue
		self.thread_stop=False
		self.queueResult=queueResult
		
	def run(self):
		while not self.thread_stop:
			try:
				task=self.queue.get_nowait()#接收消息
				xbmc.log('startsearch '+task['engine'].name+' '+task['what']+' '+str(task['page']))
			except Queue.Empty:
				self.thread_stop=True
				break
			result=task['engine'].search(task['what'],sorttype=task['sort'],page=str(task['page']))
			#plugin.notify(task['page'])
			if result['state']:
				if len(result['list'])>0:
					i=1
					for res_dict in result['list']:
						#rhash=getmagnethash(res_dict['link'])
						level=task['page']*10000+i*100+task['enginlevel']
						res_dict['level']=level
						self.queueResult.put_nowait(res_dict)
						i=i+1
			self.queue.task_done()#完成一个任务
	def stop(self):
		self.thread_stop = True


def getengineinfo(engine):
	try:
		engine_module = __import__(".".join(("engines", engine)))
		#get low-level module
		engine_module = getattr(engine_module, engine)
		#bind class name
		engine = getattr(engine_module, engine[3:])
		engine = engine()
		return {'name':engine.name,'support_sort':engine.support_sort}
	except Exception, errno:
		xbmc.log(msg='nova2err:%s'%(errno),level=xbmc.LOGERROR)
		return {}



def getmagnethash(magnet):
	result = magnet
	match = re.search(r'urn:btih:(?P<hash>[0-9a-zA-Z]{40})', magnet, re.DOTALL | re.MULTILINE | re.I)
	if match:
		result = match.group('hash')
	return result
	
def search(searchengine,what,sort,maxresult=20):
	fix_encoding()
	engines = glob(path.join(path.dirname(__file__), 'engines', '*.py'))	
	enginclasslist=[]
	for engine in engines:
		engi = path.basename(engine).split('.')[0].strip()
		if len(engi) == 0 or engi.startswith('_'):
			continue
		if searchengine!=engi and searchengine!='all':
			continue
		#plugin.notify(searchengine)
		try:
			#import engines.[engine]
			engine_module = __import__(".".join(("engines", engi)))
			# #get low-level module
			engine_module = getattr(engine_module, engi)
			# #bind class name
			engineclass = getattr(engine_module, engi[3:])
			engineclass = engineclass()
			enginclasslist.append(engineclass)
		except:
			pass

	tasklist = Queue.Queue()
	queueResult=Queue.Queue()
	
	workers = []
	for i in range(40):
		worker=workerSearch(tasklist,queueResult)
		workers.append(worker)
		
	for engineclass in enginclasslist:
		enginlevel=0
		if engineclass.page_result_count==0:
			engineclass.page_result_count=maxresult
		pagecount=int(maxresult/engineclass.page_result_count)
		if maxresult%engineclass.page_result_count>0:
			pagecount=pagecount+1
		for page in range(1,pagecount+1):
			tasklist.put({'engine':engineclass,'what':what,'sort':sort,'page':page,'enginlevel':enginlevel})
		enginlevel=enginlevel+1
		
	for worker in workers:
		worker.start()

	for worker in workers:
		worker.join()

	resultlist={}
	while not queueResult.empty():
		res_dict=queueResult.get_nowait()
		rhash=getmagnethash(res_dict['link'])
		if not resultlist.has_key(rhash):
			resultlist[rhash]=res_dict
		queueResult.task_done()
		
	def getlevel(dict):
		return dict['level']
	return sorted( resultlist.values(), key=getlevel)
	'''
	for page in range(1,5):
		enginlevel=0
		for engineclass in enginclasslist:
			try:
				if nextpage[enginlevel]:
					t=threading.Thread(target=engineclass.search)
					result=engineclass.search(what,sorttype=sort,page=page)
					if result['state']:
						if len(result['list'])>0:
							i=1
							for res_dict in result['list']:
								rhash=getmagnethash(res_dict['link'])
								#plugin.notify(rhash)
								if not resultlist.has_key(rhash):
									level=page*10000+i*100+enginlevel
									res_dict['level']=level
									resultlist[rhash]=res_dict
									i=i+1
							if len(resultlist)>=maxresult:
								break
						nextpage[enginlevel]=False
						if result.has_key('nextpage'):
							if result['nextpage']:
								nextpage[enginlevel]=True
								
			except:
				pass
			enginlevel=enginlevel+1
		else:
			page=page+1
			continue
			
		break
	def getlevel(dict):
		return dict['level']
	return sorted( resultlist.values(), key=getlevel)
	'''