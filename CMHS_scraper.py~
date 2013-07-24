from BeautifulSoup import BeautifulSoup as bs
import os, re, sys

url="https://www.sites.google.com/site/cmhskathmandu/home/cmhs-news"
page=urllib2.urlopen(url)
soup = bs(page.read())

# get all the images
soup.findAll('img')

# get the little bugger
urlretrieve(soup.findAll('img')[1]['src'], "test.png")


# loop the bitch
outpath="/Users/malindgren/Documents/CMHS"

for i in soup.findAll('img'):
	print i['src']
	try:
		urlretrieve(i['src'], os.path.join(outpath,"images",i['src'].split('/')[-1]))
	except:
		pattern = re.compile('\?')
		f = re.search(pattern, i['src']).start()
		urlretrieve(i['src'][0:f], os.path.join(outpath,"images",i['src'][0:f]))
	finally:
		print(i['src'] + "  " + "FAILED!")
		pass


# make a function (not working)

def searchSoup(url, element, outpath):
	# import some mods
	from BeautifulSoup import BeautifulSoup as bs
	import os, re, sys, urllib2
	from urllib import urlretrieve

	# get the page
	page = urllib2.urlopen(url)
	soup = bs(page.read())
	
	# now retrieve the elements that match
	for i in soup.findAll(element):
		try:
			urlretrieve(i['src'], os.path.join(outpath,"images",i['src'].split('/')[-1]))
		except:
			pattern = re.compile('\?')
			f = re.search(pattern, i['src']).start()
			urlretrieve(i['src'][0:f], os.path.join(outpath,"images",i['src'][0:f]))
		else:
			print(i['src'] + "  " + "FAILED!")
			pass




