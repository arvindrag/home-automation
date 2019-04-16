import requests
from bs4 import BeautifulSoup
import re

class TPBParser:
	API = 'https://openpirate.org'
	def __init__(self, logger):
		self.logger = logger

	def get_page(self, encoded_term):
		url = self.API+'/search/{}'.format(encoded_term)
		self.logger.info("Scraping {}".format(url))
		resp = requests.get(url)
		return resp.text

	# def get_tag_content(self, text, tag, props):
	# 	propstrs = ['{}="{}"'.format(k,props[k]) for k in props]
	# 	otag = '<{}>'.format(' '.join([tag] + propstrs))
	# 	ctag = '</{}>'.format(tag)
	# 	pat = r"""{otag}(.*){ctag}""".format(otag=otag, ctag=ctag)
	# 	return re.search(pat, text, re.DOTALL).groups()

	# This is a terrible way to do this the best way would be to 
	# have a an algo to scrape the term->seed mappings
	# and choose the best term-seed pair (since 720 is a better term)
	# and more seeds is better. but here we are
	def get_magnet_links(self, encoded_term):
		try:
			soup = BeautifulSoup(self.get_page(encoded_term+"%20720p", 'html.parser'))
			mags = soup.find_all(href=re.compile('magnet'))
			number=re.compile(r'[0-9]+')
			maglinks=list()
			for mag in mags:
				href = mag['href']
				seeders,leechers = filter(number.match, mag.parent.parent.stripped_strings)
				maglinks.append((href,seeders,leechers))
			best = max(maglinks, key=lambda a: a[2])
			return best[0]
		except:
			soup = BeautifulSoup(self.get_page(encoded_term, 'html.parser'))
			return soup.find_all(href=re.compile('magnet'))[0]['href']
		

