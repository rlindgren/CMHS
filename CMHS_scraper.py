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
	URL = 'http://www.google.com'
try:
	i = re.search('\/', URL[8:]).start()
	HOSTNAME = URL[:i + 8]
except: 
	HOSTNAME = URL

# hostname without https?://w?w?w?.?
SITEHOST = re.match('https?://w?w?w?\.?(.*)/?.*?$', HOSTNAME).group(1)
# clean up the hostname for use as directory name
CLEANHOST = SITEHOST.replace('.', '')
# path for main scrape dump directory
FILEPATH = os.path.join(FILEPATH, CLEANHOST)

print FILEPATH, HOSTNAME, SITEHOST, CLEANHOST

# make directories to hold the goods and move to base dir (FILEPATH)
try:
	os.mkdir(FILEPATH); os.chdir(FILEPATH)
	try: 
		os.mkdir('media'); os.mkdir('text')
	except: 
		if not os.access('media', os.F_OK):
			raise IOError("Could not create necessary directories. Try the command with 'sudo'.")
except: 
	try:
		os.chdir(FILEPATH)
		try: 
			os.mkdir('media'); os.mkdir('text')
		except: pass
	except: raise IOError("Error creating directories. Permissions. Try again with 'sudo'.")

# store site map
siteMap = []
siteSoup = []

# all text and resource paths
allText = ""
allResources = []

def getSoup(url):
	return bs(urllib2.urlopen(url).read())

def populateSiteMapArray(souped):
	links = souped.findAll('a')
	try: 
		anchors = list(a['href'] for a in links)
	except:
		anchors = []
		for a in links:
			try:
				a = a['href']
				anchors.append(a)
			except: pass
	#store only links under the hostname
	for a in anchors:
		if len(a) > 0:
			if SITEHOST in a: 
				siteMap.append(a)
			if a[0] is '/': 
				siteMap.append(os.path.join(HOSTNAME, a[1:]))

def expandSiteMapAndGetSiteSoup(siteMap):
	for a in siteMap:
		try: souper = getSoup(a)
		except: souper = ''
		if not souper is '' and not souper in siteSoup:
			siteSoup.append(souper)
		populateSiteMapArray(souper)

def getTheGoods(souped):
	global allText, allResources
	media = ['img', 'svg', 'video', 'picture']
	outText = souped.text
	outFiles = []
	goods = souped.findAll(media)
	# get resource paths
	for el in goods:
		try:
			src = el['src']
			if src not in allResources:
				if src[0] is '/':
						outFiles.append(os.path.join(HOSTNAME, src))
				else:
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
	os.chdir(os.path.join(FILEPATH, "text"))
	# open/create the file before writing to it
	textfile = os.open(filename, os.O_RDWR|os.O_CREAT)
	#convert from unicode to ascii
	os.write(textfile, text.encode("ascii", "ignore"))
	os.close(textfile)

def _saveMedia(file_array):
	if len(URL.split('/')[-1]) > 0:
		dirname = URL.split('/')[-1].replace('.', '')
	else:
		dirname = 'home'
	mp = re.search('.', dirname)
	if mp.start(): 
		dirname = dirname[:mp.start()] + str(time.clock()).replace('.', '')
	else:
		dirname = dirname + str(time.clock()).replace('.', '')
	# do IO
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
print('Populating Site Map...')
populateSiteMapArray(soup)
print('Expanding site map and stewing site soup...')
expandSiteMapAndGetSiteSoup(siteMap)
print siteMap
print('Getting the goods...')
for a in siteSoup:
	getTheGoods(a)
print('Scrape complete.')
