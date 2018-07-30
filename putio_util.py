import requests
import logging
import json
import time

class PutIO:
	FETCH_WAIT_SECONDS = 30
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
		self.logger.info("Checking mp4 for file: {}".format(fileid))
		url = "{}/files/{}/hls/media.m3u8".format(self.API, fileid)
		response = requests.get(url, params = {'oauth_token':self.token})
		if response.status_code !=200:
			self.logger.info("URL: {} Response: {}".format(url, response.json()))
		return [l for l in response.text.split('\n') if 'http' in l][0]

	def check_xfer(self, xfer_id):
		url = "{}/transfers/{}".format(self.API, xfer_id)
		resp = requests.get(url, params = {'oauth_token':self.token})
		return resp.json()

	def add(self, magnet):
		url = "{}/transfers/add".format(self.API)
		post = requests.post(url, data = {'url' : magnet, 'save_parent_id':0, 'oauth_token':self.token})
		return post.json()

	def add_and_await(self, magnet, await=True):
		self.logger.info("Adding link")
		xfer = self.add(magnet)
		if xfer.get('extra') and xfer['extra'].get('existing_id'):
			xisting = xfer['extra'].get('existing_id')
			xfer = self.check_xfer(xisting)
		self.logger.info(json.dumps(xfer, indent=2))
		xfer_id = xfer['transfer']['id']
		if await:
			self.logger.info("awaiting xfer")
			fileid = None
			for i in range(self.FETCH_WAIT_SECONDS*2):
				time.sleep(0.5)
				if fileid==None:				
					xfer = self.check_xfer(xfer_id)
					if xfer['transfer']['status'] == 'COMPLETED':
						self.logger.info("xfer completed")
						fileid = xfer['transfer']['file_id']
					if xfer['transfer']['down_speed'] == 0:
						return None
				else:
					self.logger.info("returning name, link")
					return xfer['transfer']['name']

