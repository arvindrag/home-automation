import requests
import re

class TPBParser:
	API = 'https://openpirate.org/'
	def __init__(self, logger):
		self.logger = logger

	def get_page(self, encoded_term):
		url = self.API+'/search/{}/0/99/0'.format(encoded_term)
		self.logger.info("Scraping {}".format(url))
		resp = requests.get(url)
		return resp.text.replace('>','>\n')

	def get_tag_content(self, text, tag, props):
		propstrs = ['{}="{}"'.format(k,props[k]) for k in props]
		otag = '<{}>'.format(' '.join([tag] + propstrs))
		ctag = '</{}>'.format(tag)
		pat = r"""{otag}(.*){ctag}""".format(otag=otag, ctag=ctag)
		return re.search(pat, text, re.DOTALL).groups()

	# This is a terrible way to do this the best way would be to 
	# have a an algo to scrape the term->seed mappings
	# and choose the best term-seed pair (since 720 is a better term)
	# and more seeds is better. but here we are
	def get_magnet_links(self, encoded_term):
		try:
			self.get_page(encoded_term+"%20720p")
			page_text = self.get_page(encoded_term)
			results = self.get_tag_content(page_text, 'table', {'id':'searchResult'})[0]
			return re.findall(r'<a href="(magnet:[^"]*)"', results)
		except:
			self.get_page(encoded_term)
			page_text = self.get_page(encoded_term)
			results = self.get_tag_content(page_text, 'table', {'id':'searchResult'})[0]
			return re.findall(r'<a href="(magnet:[^"]*)"', results)
		

