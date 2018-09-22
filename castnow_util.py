import threading
import subprocess

class CastNow:
	DEVICE_MAP = {
		'BED_ROOM':'192.168.7.22',
		'LIVING_ROOM':'192.168.7.88',
		'TV':'192.168.7.20'
	}

	RUN = '/usr/local/bin/castnow'

	def __init__(self, logger, dryrun = False):
		self.logger = logger
		self.dryrun = dryrun

	def cast(self, things, timeout_sec = 25, device='TV'):
		if self.dryrun:
			self.logger.info("Not Casting: {}".format(things))
		else:
			self.logger.info("Casting: {}".format(things))
			cmd = [self.RUN, '--address', self.DEVICE_MAP[device], things]
			self.logger.info("casting: {}".format(' '.join(cmd)))
			proc = subprocess.Popen(cmd, 
				stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			timer = threading.Timer(timeout_sec, proc.kill)
			try:
				timer.start()
				stdout, stderr = proc.communicate()
			finally:
				timer.cancel()
