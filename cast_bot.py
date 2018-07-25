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
		self.nocast = nocast
		self.creds = creds
		self.telebot = telepot.Bot(self.creds["creds"]["telegram_bot_token"])
		self.putio = PutIO(self.creds["creds"]["put_io_token"], self.logger)
		self.castnow = CastNow(self.logger)
		self.logger.info('Starting up the cast bot...')
	
	def pars(self, msg):
		msg = re.sub(r'[^a-zA-Z0-9\s]', '', msg)
		m = re.match(self.EPPAT, msg)
		if m:
			string, season, episode = m.groups()
			options = ["%s S%02dE%02d"%(string, int(season), int(episode)), "%s %s%s"%(string, int(season), int(episode))]
		else:
			options = [msg.replace(' ', '%20')]
		options = [o.replace(' ', '%20') for o in options]
		return options

	def handle(self, msg):
		self.logger.info("Received msg: \n{}".format(json.dumps(msg, indent=2)))
		m = re.match(self.SEARCHPAT, msg['text'])
		if m:
			self.logger.info('looking for {}'.format(m.groups()[0]))
			options = self.pars(m.groups()[0])
			self.logger.info('looking for {}'.format(options))
			mp4s = list()
			for o in options:
				for f in self.putio.search(o)['files']:
					if f["is_mp4_available"]:
			 			mp4s.append(f)			 			
			self.logger.info("Files found: \n{}".format(',\n'.join([mp4['name'] for mp4 in mp4s])))
			if mp4s:
				links = [self.putio.link(m['id']) for m in mp4s]
				if not self.nocast:
					self.castnow.cast(links)
			else:
				self.logger.info("No mp4s found :( ...")

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
	print MyBot(creds, logger, True).handle({"text":"SEARCHFOR: Legion season 2 episode 10"})

if __name__ == '__main__':
	main() 
	# test()