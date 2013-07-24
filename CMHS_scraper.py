#!/usr/bin/python

# import some dependencies
import os, re, sys, urllib2, time
from urllib import urlretrieve

# some python installations include beautifulsoup4 as bs4...
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
		if sys.argv[2] == '.': FILEPATH = os.getcwd()
		else: FILEPATH = sys.argv[2]
	else:
		FILEPATH = os.getcwd()
		try: 
			newdir = os.mkdir(URL)
			os.chdir(URL)
		except: pass
else:
	URL = 'https://www.sites.google.com/site/cmhskathmandu'
	FILEPATH = os.getcwd()

try:
	i = re.search('\/', URL[8:]).start()
	HOSTNAME = URL[:i + 8]
except: 
	HOSTNAME = URL

# hostname without https?://w?w?w?.?
SITEHOST = re.match('https?://w?w?w?\.?(.*)/?.*?$', HOSTNAME).group(1)
# clean up the hostname for use as directory name
CLEANHOST = SITEHOST.replace('.', '')
# path for main dump directory
FILEPATH = os.path.join(FILEPATH, CLEANHOST)

# make directories to hold the goods and move to base dir (FILEPATH)
try:
	os.mkdir(FILEPATH)
	try: 
		os.mkdirs(os.path.join(FILEPATH,'media')); os.mkdirs(os.path.join(FILEPATH,'text'))
	except: 
		if not os.access('media', os.F_OK) or not os.access('text', os.F_OK):
			raise IOError("Could not create necessary directories. Try the command with 'sudo'.")
except: 
	try:
		os.chdir(FILEPATH)
		try: 
			os.mkdir('media'); os.mkdir('text')
		except: pass
	except: raise IOError("Error creating directories. Permissions. Try again with 'sudo'.")

MEDIAPATH = os.path.join(FILEPATH,'media')
TEXTPATH = os.path.join(FILEPATH,'text')

# store site map
siteMap = []
siteSoup = []

# all text and resource paths
allText = ""
allResources = []

def getSoup(url):
	return bs(urllib2.urlopen(url).read())

def populateSiteMapArray(soup):
	_expandSiteMap(soup.findAll('a'))

def _expandSiteMap(links):
	global siteMap, URL
	if len(links) > 0:
		try: 
			a = str(links[0]['href'])
			y = a.split('/')
			t = re.search('\?', y[-1])
			if URL in a and not a in siteMap and not t.start(): 
				siteMap.append(a)
			if a[0] is '/' and os.path.join(HOSTNAME, a[1:]) not in siteMap: 
				siteMap.append(os.path.join(HOSTNAME, a[1:]))
		except: pass
		_expandSiteMap(links[1:])
	
def getSiteSoup(links):
	for a in links:
		try: s = getSoup(a)
		except: s = False
		if s and not s in siteSoup:
			siteSoup.append(s)

def getTheGoods(soup):
	global allText, allResources
	media = ['img', 'svg', 'video', 'picture']
	outText = soup.find('div', {'id': 'sites-chrome-main-wrapper'}).text.encode('ascii', 'ignore')
	outFiles = []
	goods = soup.findAll(media)
	# get resource paths
	for el in goods:
		try:
			src = el['src']
			if str(src)[0] is '/':
				src = os.path.join(HOSTNAME, src[1:]) 
			if src not in allResources and src not in outFiles:
				outFiles.append(src)
			else: pass
		except: pass
	# retain a store of all resource paths, so no repeats!
	allResources += outFiles
	_writeText(outText)
	_saveMedia(outFiles)

def _writeText(text):
	if len(URL.split('/')[-1]) > 0:
		filename = URL.split('/')[-1].replace('.', '')
	else:
		filename = 'home'
	# do some work to the filename to make it valid
	mp = re.search('.', filename)
	if mp.start(): 
		filename = filename[:mp.start()]
	else:
		filename = filename + '_' + str(time.clock()).replace('.', '') + '.txt'
	# do IO stuffs...
	os.chdir(TEXTPATH)
	# open/create the file before writing to it
	textfile = os.open(filename, os.O_RDWR|os.O_CREAT)
	#convert from unicode to ascii
	os.write(textfile, text.encode("ascii", "ignore"))
	os.close(textfile)

def _saveMedia(file_array):
	# create and navigate to a new directory
	SAVEPATH = MEDIAPATH
	os.chdir(SAVEPATH)
	# retrieve the elements that match
	for media in file_array:
		try:
			urlretrieve(media, media.split('/')[-1])
		except:
	 		pattern = re.compile('\?')
	 		f = re.search(pattern, media)
	 		try:
		 		if f.start():
		 			f = f.start()
					urlretrieve(media[:f], media.split('/')[-1][:f])
				else:
					print("\t'" + media + "'  " + "FAILED!")
			except: print("\t'" + media + "'  " + "FAILED!")

# execution
print('Populating Site Map...')
populateSiteMapArray(getSoup(URL))
print('Concocting Site Map Soup...')
getSiteSoup(siteMap)
print('Getting The Goods...')
for a in siteSoup:
	getTheGoods(a)
print('Scrape Complete!')
print "\t", len(allResources), 'media objects were saved at', MEDIAPATH
print "\t", len(siteMap), 'text files were saved at', TEXTPATH
