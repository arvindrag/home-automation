import re
import json
import time
import requests
import telepot
import urllib
import subprocess
from telepot.loop import MessageLoop

class PutIO:
	def __init__(self, token):
		self.API = "https://api.put.io/v2"
		self.token = token

	def search(self, string):
		url = "{}/files/search/{}".format(self.API, string)
		print url
		response = requests.get(url, params = {'oauth_token':self.token})
		return response.json()

	def link(self, fileid):
		url = "{}/files/{}/hls/media.m3u8".format(self.API, fileid)
		response = requests.get(url, params = {'oauth_token':self.token})
		return [l for l in response.text.split('\n') if 'http' in l][0]

class CastNow:
	BEDROOM = '192.168.7.22'
	DEFAULT = BEDROOM
	RUN = '/usr/local/bin/castnow'

	def cast(self, thing):
		subprocess.call([self.RUN, '--address', self.DEFAULT, thing])


class MyBot:
	SEARCHPAT = r".*SEARCHFOR:(.*)"
	def __init__(self, credsfile):
		self.creds = json.loads(open(credsfile, "r").read())
		self.bot = telepot.Bot(self.creds["creds"]["telegram_bot_token"])
		self.putio = PutIO(self.creds["creds"]["put_io_token"])
		self.castnow = CastNow()
		print 'starting...'

	def pars(self, msg):
		sofar = list()
		for c in msg:
			if c.isalnum():
				sofar.append(c)
			elif c == ' ':
				sofar.append('%20')
			else:
				pass
		return ''.join(sofar)


	def handle(self, msg):
		m = re.match(self.SEARCHPAT, msg['text'])
		if m:
			tofind = self.pars(m.groups()[0])
			print 'looking for ' + tofind
			mp4s = [f for f in self.putio.search(tofind)['files'] if f["is_mp4_available"]]
			print json.dumps(mp4s, indent=4)
			link = self.putio.link(mp4s[0]['id'])
			self.castnow.cast(link)

	def run(self):
		MessageLoop(self.bot, self.handle).run_as_thread()

def main():
	try:
		MyBot("my.creds").run()
		while True:
			time.sleep(20)
	except KeyboardInterrupt:
		print 'done'
		exit(0)

if __name__ == '__main__':
	main()