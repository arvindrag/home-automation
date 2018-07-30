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
from tpb_parser import TPBParser

def isint(num):
	try:
		i = int(num)
		return True
	except:
		return False

class MyBot:
	SEARCHPAT = r".*SEARCHFOR:(.*)"
	EPPAT = r"(.*)season ([0-9]+) episode ([0-9]+)"
	def __init__(self, creds, logger, nocast = False):
		self.logger = logger
		self.logger.info('Starting up the cast bot...')
		self.nocast = nocast
		self.creds = creds
		self.telebot = telepot.Bot(self.creds["creds"]["telegram_bot_token"])
		self.putio = PutIO(self.creds["creds"]["put_io_token"], self.logger)
		self.castnow = CastNow(self.logger, nocast)
		self.tpb = TPBParser(self.logger)
		
	
	def pars(self, msg):
		msg = re.sub(r'[^a-zA-Z0-9\s]', '', msg)
		m = re.match(self.EPPAT, msg)
		if m:
			string, season, episode = m.groups()
			options = ["%s S%02dE%02d"%(string, int(season), int(episode))]
		else:
			options = [msg.replace(' ', '%20')]
		options = [o.replace(' ', '%20') for o in options]
		return options

	def handle(self, msg):
		self.logger.info("Received msg: \n{}".format(json.dumps(msg, indent=2)))
		m = re.match(self.SEARCHPAT, msg['text'])
		if m:
			searchtext = m.groups()[0]
			self.logger.info('looking for {}'.format(searchtext))
			schtext = self.pars(searchtext)[0]
			self.logger.info('looking for {}'.format(schtext))
			magnet = self.tpb.get_magnet_links(schtext)[0]
			name = self.putio.add_and_await(magnet)
			self.logger.info("File found: {}".format(name))

			fileses = self.putio.search(schtext)['files']
			mp4s = [f for f in fileses if f['is_mp4_available']]
			self.logger.info("attempting castnow")
			self.castnow.cast(self.putio.link(mp4s[0]['id']))


	def start_msg_loop(self):
		self.logger.info("Starting msg handler loop..")
		MessageLoop(self.telebot, self.handle).run_as_thread()

def setup():
	logging.config.fileConfig('logging.ini')
	logger = logging.getLogger(__name__)
	creds = json.loads(open("my.creds", "r").read())
	return creds, logger

def main():
	try:
		creds, logger = setup()
		logger.info("Starting cast bot..")
		MyBot(creds, logger).start_msg_loop()
		while True:
			time.sleep(20)
	except KeyboardInterrupt:
		print 'done'
		exit(0)

def test():
	creds, logger = setup()
	print MyBot(creds, logger, True)

if __name__ == '__main__':
	main() 
	# test()