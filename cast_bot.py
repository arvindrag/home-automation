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
	ADD_AND_CAST_PAT = 	r"/ADDCAST:(.*)"
	SEARCHPAT = 	r"/SEARCHCAST:(.*)"
	JUSTADDPAT = 	r"/JUSTADD:(.*)"
	CLEANPAT = 	r"/CLEAN:(.*)"
	def ACTION_MAP(self): 
		dic = {
		self.ADD_AND_CAST_PAT: self.add_and_cast,
		# SEARCHPAT: self.search_and_cast,
		self.JUSTADDPAT: self.just_add
		# CLEAN: self.clean
		}
		return dic
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
			options = "%s S%02dE%02d 720p"%(string, int(season), int(episode))
		else:
			options = msg
		return options.replace(' ', '%20')

	def mp4s(files):
		mp4s = [f for f in fileses if f['is_mp4_available'] or f["content_type"]=="video/mp4"]
		return mp4s

	def add_and_cast(self, searchstr, wait=120):
		self.logger.info('add and cast for {}'.format(searchstr))
		self.logger.info('looking for {}'.format(searchstr))
		magnet = self.tpb.get_magnet_links(searchstr)
		name = self.putio.add_and_await(magnet)
		self.logger.info("File found: {}".format(name))

		start = time.time()
		while(time.time()<start+wait):
			fileses = self.putio.search(searchstr)['files']
			mp4s = [f for f in fileses if f['is_mp4_available']]
			if(len(mp4s(fileses))<1):
				if(fileses>0):
					self.logger.info("files but no mp4!")	
				continue
			else:
				self.logger.info("attempting castnow")
				self.castnow.cast(self.putio.link(mp4s[0]['id']))
				break
			

	def just_add(self, searchstr):
		self.logger.info('add and cast for {}'.format(searchstr))
		self.logger.info('looking for {}'.format(searchstr))
		magnet = self.tpb.get_magnet_links(searchstr)
		name = self.putio.add(magnet)

	# def clean(self, searchstr):
	# 	files = self.putio.search(searchstr)
	# 	for f in files:
	# 		self.putio.

	def handle(self, msg):
		self.logger.info("Received msg: \n{}".format(json.dumps(msg, indent=2)))
		for pat in self.ACTION_MAP():
			m = re.match(pat, msg['text'])
			if m:
				searchstr = self.pars(m.groups()[0])
				action = self.ACTION_MAP()[pat]
				action(searchstr)

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
	print json.dumps(MyBot(creds, logger, True).putio.search("Lord of the rings")['files'], indent=4)

if __name__ == '__main__':
	main() 
	# test()