import requests
import re

class TPBParser:
	API = 'https://pirateproxy.fun'
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

	def get_magnet_links(self, encoded_term):
		page_text = self.get_page(encoded_term)
		results = self.get_tag_content(page_text, 'table', {'id':'searchResult'})[0]
		return re.findall(r'<a href="(magnet:[^"]*)"', results)
		

