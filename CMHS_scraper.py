#!/usr/bin/python

# import some dependencies
import os, re, sys, urllib2, time
from urllib import urlretrieve

# some python installations include beautifulsoup4...
try: 
	from bs4 import BeautifulSoup as bs
except: 
	try:
		from BeautifulSoup import BeautifulSoup as bs
	except:
		raise NameError("Couldn't find 'Beautiful Soup' module.\nRun 'pip install beautifulsoup4'")

# set resource paths
if (len(sys.argv) > 1):
	URL = sys.argv[1]
	if (len(sys.argv) > 2): 
		FILEPATH = sys.argv[2]
	else:
		FILEPATH = os.getcwd()
		try: 
			newdir = os.mkdir(URL)
			os.chdir(URL)
		except: pass
else:
	URL = 'http://www.google.com'
try:
	i = re.search('\/', URL[8:]).start()
	HOSTNAME = URL[:i + 8]
except: 
	HOSTNAME = URL

# make directories
os.chdir(FILEPATH)
try: os.mkdir('media'); os.mkdir('text')
except OSError: pass

# html tags to search through for resources
media = ['img', 'svg', 'video', 'picture']
text = ['div', 'article', 'p', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'font']

# store site map
siteMap = []
siteSoup = []

# all text and resource paths
allText = ""
allResources = []

def getSoup(url):
	page = urllib2.urlopen(url)
	soup = bs(page.read())
	siteSoup.append(soup)
	return soup

def populateSiteMapArray(souped):
	pattern = re.compile(URL)
	try:
		anchors = list(str(a['href']) for a in souped.findAll('a'))
	except:
		anchors = []
		for a in souped.findAll('a'):
			try:
				anchors.append(str(a['href']))
			except:
				pass
	for a in anchors:
		if not a in siteMap and (re.search(pattern, a) > -1 or re.search('^/', a)):
			if a[0] is '/': a = HOSTNAME + a
			if not re.search('\?', a) and not re.search('system', a): 
				siteMap.append(a)

def expandSiteMapAndGetSiteSoup():
	for a in siteMap:
		getSoup(a)

def getTheGoods(souped):
	global allText, allResources
	outText = ""
	outFiles = []
	goods = souped.findAll(media + text)
	for el in goods:
		# only download if unique
		if el.text not in allText:
			outText += el.text
		try:
			if el['src'] not in allResources:
				outFiles.append(el['src'])
			else: pass
		except: pass
	# retain a store of all text and resource paths for the site, so no repeats!
	allText += outText
	allResources += outFiles
	_writeText(outText)
	_saveMedia(outFiles)

def _writeText(text):
	filename = URL.split('/')[-1]
	mp = re.search('.', filename)
	if mp: 
		filename = filename[:mp.start()]
	else:
		filename = filename + '_' + str(time.clock()).replace('.', '') + '.txt'
	os.chdir(os.path.join(FILEPATH, "text"))
	textfile = os.open(filename, os.O_RDWR|os.O_CREAT)
	os.write(textfile, text.encode("ascii", "ignore"))
	os.close(textfile)

def _saveMedia(file_array):
	dirname = URL.split('/')[-1]
	mp = re.search('.', dirname)
	if mp: 
		dirname = dirname[:mp.start()] + str(time.clock()).replace('.', '')
	else:
		dirname = dirname + str(time.clock()).replace('.', '')
	os.chdir(os.path.join(FILEPATH, "media"))
	# create and navigate to a new directory
	os.mkdir(dirname); os.chdir(dirname)
	# retrieve the elements that match
	for media in file_array:
		try:
			urlretrieve(media, os.path.join(os.getcwd(), media.split('/')[-1]))
		except:
	 		pattern = re.compile('\?')
	 		try:
	 			f = re.search(pattern, media).start()
		 		try:
					urlretrieve(media[:f], os.path.join(os.getcwd(), media[0:f]))
				except:
					print(media + "  " + "FAILED!")
			except: print(media + "  " + "FAILED!")

# execution
print('Scrape in progress...')
soup = getSoup(URL)
populateSiteMapArray(soup)
print('Expanding site map...')
expandSiteMapAndGetSiteSoup()
print('Getting the goods...')
for a in siteSoup:
	getTheGoods(a)
print('Scrape complete.')
