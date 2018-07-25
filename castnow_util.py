import threading
import subprocess

class CastNow:
	BEDROOM = '192.168.7.22'
	DEFAULT = BEDROOM
	RUN = '/usr/local/bin/castnow'

	def __init__(self, logger):
		self.logger = logger

	def cast(self, things, timeout_sec = 25):
		cmd = [self.RUN, '--address', self.DEFAULT] + things
		self.logger.info("casting: {}".format(' '.join(cmd)))
		proc = subprocess.Popen(cmd, 
			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		timer = threading.Timer(timeout_sec, proc.kill)
		try:
			timer.start()
			stdout, stderr = proc.communicate()
		finally:
			timer.cancel()
