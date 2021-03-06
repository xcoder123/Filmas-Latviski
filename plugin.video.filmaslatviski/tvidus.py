# -*- coding: utf-8 -*-
import network
import sys
import xbmc
import xbmcgui
import xbmcplugin
import re
import urlresolver
import CommonFunctions
import kodi_func
import cfscrape
import requests
import tempfile
import shutil
import base64

common = CommonFunctions
common.plugin = "Filmas-Latviski-1.0.0"

mySourceId = 2

#important this website uses DDoS prevention mechanism
#https://github.com/Anorov/cloudflare-scrape

mainURL = 'http://tvid.us/movies'

def SearchRaw(searchStr):
	result = []
	
	if searchStr == False or len(searchStr) == 0: return result
	
	session = requests.session()
	scraper = cfscrape.create_scraper(sess=session)
	html = scraper.get("http://tvid.us/movies/search/"+str(searchStr)).content
	moviesList = common.parseDOM(html, "div", attrs = { "class": "modal-content" })
	moviesTitleList = common.parseDOM(moviesList, "h4")
	moviesThumbnailURLsList = common.parseDOM(moviesList, "img", attrs = { "class": "img-responsive" }, ret = "src")
	moviesURLs = common.parseDOM(moviesList, "a", ret = "href", attrs = { "class": "btn btn-primary" })
	# print moviesThumbnailURLsList
	print moviesURLs, len(moviesURLs)
	
	
	for i in range(0, len(moviesURLs)):
		localFile = None
		try:
			rawImage = scraper.get("http:"+moviesThumbnailURLsList[i], stream=True)
			rawImage.decode_content = True	
			localFile = xbmc.translatePath('special://temp/'+moviesThumbnailURLsList[i].split("/")[-1] )
			temp = open( localFile, mode='wb')
			shutil.copyfileobj(rawImage.raw, temp)
			temp.close()
			print localFile
		except:
			pass
			
		result.append({
			'title': moviesTitleList[i].encode('utf-8'),
			'url': moviesURLs[i],
			'thumb': localFile,
			'state': 'state_play',
			'source_id': mySourceId
		})	
	
	return result
		
	
def Search(searchStr = None):
	if searchStr == None:
		text = kodi_func.showkeyboard('', u'Meklēt filmu')
	else:
		text = searchStr
	print "Search string: " + text
	
	results = SearchRaw(text)
	
	for r in results:
		kodi_func.addDir(r['title'], r['url'], 'state_play', r['thumb'], source_id=r['source_id'])
		
		
	# if len(results) >= 27:
		# kodi_func.addDir("Nākamā Lapa >>", url , 'state_movies', None, str(int(page) + 1), source_id=mySourceId)
		
		
def HomeNavigation():
	print "Opening tvid.us"
	# url = 'http://tvid.us/movies'
	# html = network.getHTML(url)
	scraper = cfscrape.create_scraper()  # returns a CloudflareScraper instance	
	html = scraper.get("http://tvid.us/movies").content
	print 'html: ' + html
	# nav_links_list = common.parseDOM(html, "div", attrs = { "id": "genre-nav" })
	nav_links = common.parseDOM(html, "a", ret = "href", attrs = { "class": "btn btn-success btn-flat col-xs-12 col-sm-6 col-md-3" })
	nav_links_name = common.parseDOM(html, "a", attrs = { "class": "btn btn-success btn-flat col-xs-12 col-sm-6 col-md-3" })
	kodi_func.addDir('Meklēt', '', 'state_search', '%s/meklet2.png'% kodi_func.iconpath, source_id=mySourceId)
	kodi_func.addDir('Jaunākās Filmas | Visas Filmas', mainURL, 'state_movies', '%s/new.png'% kodi_func.iconpath, source_id=mySourceId)
		
	# pagirasList = u'https://openload.co/embed/dLuET3ML86E/Deadpool.%28Dedpuls%29.2016.720p.LAT.THEVIDEO.LV.mkv.mp4'	
	# link = urlresolver.resolve(pagirasList)
	# addDir('Dedpūls', pagirasList, 'state_play', None)
	# addLink("Dedpūls", link.encode('utf-8'), None)
	# print nav_links
	# print nav_links_name
	for i in range(0, len(nav_links)):
		if kodi_func.isLinkUseful(nav_links[i]):
			# print mainURL + nav_links[i]
			kodi_func.addDir(nav_links_name[i].encode('utf-8'), 'http:' + nav_links[i], 'state_movies', kodi_func.GetCategoryImage(nav_links_name[i]), source_id=mySourceId)
			
def Movies(url, page=1):
	session = requests.session()
	scraper = cfscrape.create_scraper(sess=session)
	html = scraper.get(url+"/page/"+str(page)).content
	# print "html" + html
	moviesList = common.parseDOM(html, "div", attrs = { "class": "modal-content" })
	moviesTitleList = common.parseDOM(moviesList, "h4")
	moviesThumbnailURLsList = common.parseDOM(moviesList, "img", attrs = { "class": "img-responsive" }, ret = "src")
	moviesURLs = common.parseDOM(moviesList, "a", ret = "href", attrs = { "class": "btn btn-primary" })
	print moviesThumbnailURLsList
	print moviesURLs, len(moviesURLs)
	
	
	for i in range(0, len(moviesURLs)):
		localFile = None
		try:
			if "http:" not in moviesThumbnailURLsList[i]:
				rawImage = scraper.get("http:"+moviesThumbnailURLsList[i], stream=True)
			else:
				rawImage = scraper.get(moviesThumbnailURLsList[i], stream=True)
			rawImage.decode_content = True	
			localFile = xbmc.translatePath('special://temp/'+moviesThumbnailURLsList[i].split("/")[-1] )
			temp = open( localFile, mode='wb')
			shutil.copyfileobj(rawImage.raw, temp)
			temp.close()
			print localFile
		except:
			pass
		kodi_func.addDir(moviesTitleList[i].encode('utf-8'), moviesURLs[i], 'state_play', localFile, source_id=mySourceId)
		
	if len(moviesURLs) >= 27:
		kodi_func.addDir("Nākamā Lapa >>", url , 'state_movies', '%s/next.png'% kodi_func.iconpath, str(int(page) + 1), source_id=mySourceId)
		
def PlayMovie(url, title, picture):
	# print url
	session = requests.session()
	scraper = cfscrape.create_scraper(sess=session)
	html = scraper.get('http:'+url).content
	# print html
	# return
	displayDiv = common.parseDOM(html, "div", attrs = { "id": "display"} )
	# print displayDiv	
	videoContainer = common.parseDOM(displayDiv[0], "iframe", ret="src")
	print "ATRASTIE VIDEO: "
	print videoContainer
	print title.decode('latin-1').encode('utf-8')
	
	#aha it's not the standard openload.co video
	print len(videoContainer)
	if len(videoContainer) == 0:
		searchObj = re.search('file: atob\("[\w\d=.,]*"\)', html)
		if searchObj:
			resolvedUrl = searchObj.group().replace('file: atob("', '')
			resolvedUrl = resolvedUrl[:-2]	
			videoContainer = [base64.b64decode(resolvedUrl)]
			print resolvedUrl, videoContainer
		else:
		   print "Well couldn't decode url"
		
	
	link = urlresolver.resolve(videoContainer[0])
	if link != False:
		kodi_func.addLink(title.decode('utf-8').encode('utf-8') + " - Latviski", link.encode('utf-8'), picture)	
	elif kodi_func.isVideoFormat(videoContainer[0].split(".")[-1]):
		kodi_func.addLink(title.decode('utf-8').encode('utf-8') + " - Latviski", videoContainer[0], picture)	
	print "LINKS: " + str(link)
	# link = re.compile('file:[\s\t]*"(.+?)"').findall(html.decode('windows-1251').encode('utf-8'))[0]