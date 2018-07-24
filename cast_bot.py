import re
import json
import time
import telepot
import urllib
from telepot.loop import MessageLoop
import logging
import logging.config

from putio_util import PutIO
from castnow_util import CastNow

class MyBot:
	SEARCHPAT = r".*SEARCHFOR:(.*)"
	def __init__(self, creds, logger):
		self.logger = logger
		self.creds = creds
		self.telebot = telepot.Bot(self.creds["creds"]["telegram_bot_token"])
		self.putio = PutIO(self.creds["creds"]["put_io_token"], self.logger)
		self.castnow = CastNow(self.logger)
		self.logger.info('Starting up the cast bot...')

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
		self.logger.info("Received msg: \n{}".format(json.dumps(msg, indent=2)))
		m = re.match(self.SEARCHPAT, msg['text'])
		if m:
			tofind = self.pars(m.groups()[0])
			self.logger.info('looking for {}'.format(tofind))
			mp4s = [f for f in self.putio.search(tofind)['files'] if f["is_mp4_available"]]
			self.logger.info("Files found: \n{}".format(',\n'.join([mp4['name'] for mp4 in mp4s])))
			link = self.putio.link(mp4s[0]['id'])
			self.castnow.cast(link)

	def start_msg_loop(self):
		self.logger.info("Starting msg handler loop..")
		MessageLoop(self.telebot, self.handle).run_as_thread()

def main():
	try:
		logging.config.fileConfig('logging.ini')
		logger = logging.getLogger(__name__)
		creds = json.loads(open("my.creds", "r").read())
		
		logger.info("Starting cast bot..")
		MyBot(creds, logger).start_msg_loop()
		while True:
			time.sleep(20)
	except KeyboardInterrupt:
		print 'done'
		exit(0)

if __name__ == '__main__':
	main()