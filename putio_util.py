import requests
import logging

class PutIO:
	def __init__(self, token, logger):
		self.logger = logger
		self.API = "https://api.put.io/v2"
		self.token = token

	def search(self, string):
		self.logger.info("searching for \"{}\"".format(string))
		url = "{}/files/search/{}".format(self.API, string)
		response = requests.get(url, params = {'oauth_token':self.token})
		rjson = response.json()
		self.logger.info("got {} results for {}".format(rjson['total'], string))
		return rjson

	def link(self, fileid):
		url = "{}/files/{}/hls/media.m3u8".format(self.API, fileid)
		response = requests.get(url, params = {'oauth_token':self.token})
		return [l for l in response.text.split('\n') if 'http' in l][0]
