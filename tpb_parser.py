import requests
import re
import random
from bs4 import BeautifulSoup

class TPBParser:
	SEARCH_URL = "{}/search/{}"
	def __init__(self, sources, logger):
		self.sources = sources
		self.logger = logger

	def get_search_soup(self, url):
		resp = requests.get(url)
		print '>', url
		print '>',resp.status_code
		return BeautifulSoup(resp.text, features="html5lib")

	def get_working_sauce(self, encoded_term):
		random.shuffle(self.sources)
		for sauce in self.sources:
			try:
				url = self.SEARCH_URL.format(sauce, encoded_term)
				self.logger.info("Trying sauce: {}".format(url))
				magnet = self.get_search_soup(url).find(href=re.compile("magnet"))
				if magnet:
					self.logger.info("Good sauce: {}".format(url))
					return sauce
			except:
				pass
		raise Exception("Unable to find working sources!")

	def get_highest_seeded(self, sauce, encoded_term):
		url = self.SEARCH_URL.format(sauce, encoded_term)
		soup_initial = self.get_search_soup(url)
		seed_ordered = soup_initial.find("a", title=re.compile("order.*seed", re.IGNORECASE))
		return sauce+seed_ordered['href']
		
	def get_magnets(self, soup):
		magnet_links = soup.find_all(href=re.compile("magnet"))
		magnets = list()
		for m in magnet_links:
			divs = m.parent.parent.find_all('td')
			leechers = int(divs[-1].text)
			seeders = int(divs[-2].text)
			magnets.append((m['href'], seeders))
		return magnets


	def get_results(self, encoded_term):
		# sauce = self.get_working_sauce(encoded_term) 
		# seed_ordered = self.get_highest_seeded(sauce, encoded_term)
		url = self.SEARCH_URL.format(self.sources[0], encoded_term)
		soup = self.get_search_soup(url)
		return self.get_magnets(soup)

def test():
	import logging
	p = TPBParser(['https://ikwilthepiratebay.org'], logging.getLogger(__name__))
	print p.get_results("daredevil") 
	# data = open("tmp.html").read()
	# soup = BeautifulSoup(data, features="html5lib")
	# rows = soup.find_all("tr")
	# magnet = row.find(href=re.compile("magnet"))
	# for row in rows:
		
	# 	if magnet: 
	# 		magnets.append(magnet)
	# 		vals = magnet.parent.parent.text
	# 		print [v.strip() for v in vals.split('\n') if len(v)>0]
	# print magnets

if __name__ == '__main__':
		test()
		

