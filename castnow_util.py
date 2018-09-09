import threading
import subprocess

class CastNow:
	BEDROOM = '192.168.7.22'
	TV = '192.168.7.20'
	DEFAULT = TV
	RUN = '/usr/local/bin/castnow'

	def __init__(self, logger, dryrun = False):
		self.logger = logger
		self.dryrun = dryrun

	def cast(self, things, timeout_sec = 25):
		if self.dryrun:
			self.logger.info("Not Casting: {}".format(things))
		else:
			self.logger.info("Casting: {}".format(things))
			cmd = [self.RUN, '--address', self.DEFAULT, things]
			self.logger.info("casting: {}".format(' '.join(cmd)))
			proc = subprocess.Popen(cmd, 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			timer = threading.Timer(timeout_sec, proc.kill)
			try:
				timer.start()
				stdout, stderr = proc.communicate()
			finally:
				timer.cancel()
