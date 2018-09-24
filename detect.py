#!/usr/bin/env python
from argparse import ArgumentParser
import json
import re
import os
import eero as eerolib
import pickle
import time
import logging
import logging.config
from datetime import datetime
import telepot
import subprocess
from castnow_util import CastNow
from systemd.journal import JournalHandler

class CookieStore(eerolib.SessionStorage):
    def __init__(self, cookie_file):
        from os import path
        self.cookie_file = path.abspath(cookie_file)
        try:
            with open(self.cookie_file, 'r') as f:
                self.__cookie = f.read()
        except IOError:
            self.__cookie = None
    @property
    def cookie(self):
        return self.__cookie
    @cookie.setter
    def cookie(self, cookie):
        self.__cookie = cookie
        with open(self.cookie_file, 'w+') as f:
            f.write(self.__cookie)

class Memory:
    def __init__(self, path, logger):
        self.logger = logger
        self.path = path
        if os.path.isfile(self.path):
            logger.info("found memory file, loading")
            infile = open(self.path, "rb")
            self.store = pickle.load(infile)
            infile.close()
        else:
            logger.info("no memory file, starting clean")
            self.store = dict()
        self.logger.info("initalized memory!")

    def memorize(self):
        outfile = open(self.path, "wb")
        pickle.dump(self.store, outfile)
        self.logger.info("store is dumped")

    def recall(self, key):
        return self.store.get(key)

    def remember(self, kv):
        self.store.update(kv)
        self.store['stored'] = time.time()
        self.memorize()

class Detector:

    AWAY_THRESHOLD_SECS = 400
    SLEEP = 2
    ERROR = 4
    EPOCH0 = datetime(1970,1,1)

    def to_utc_epoch(self, datetime):
        return (datetime - self.EPOCH0).total_seconds()

    def check_phones(self, devices):
        PHONEPAT = r".*(phone).*"
        phones = [d for d in devices if d['hostname'] and re.match(PHONEPAT, d['hostname'], re.IGNORECASE)]
        live = [p for p in phones if p['connected']]
        now = time.time()
        returned = list()
        self.logger.info("{} devices on network".format(len(live)))
        stored = self.memory.recall('stored')
        for l in live:
            lastseen = self.memory.recall(l['hostname'])
            if not lastseen:
                self.logger.info("live device: {} never seen, zero".format(l['hostname']))
                lastseen = 0
                
            secsago = now - lastseen
            self.logger.info("live device: {}: last seen {} seconds ago({})".format(
                l['hostname'], int(secsago), int(lastseen)))
            if secsago > (self.AWAY_THRESHOLD_SECS):
                self.logger.info("device {} seen > {} seconds ago! appending!".format(l['hostname'], secsago, self.AWAY_THRESHOLD_SECS))
                returned.append(l['hostname'])
            else:
                self.logger.info("{} seen only {} seconds ago".format(l['hostname'], secsago))
        status = dict([(l['hostname'], now) for l in live])
        self.memory.remember(status)
        return returned

    def detect(self):
        while True:
            devices = self.eero.devices(self.network['url'])
            returned = self.check_phones(devices)
            self.logger.info("returned device(s) found: {}".format(returned))
            if len(returned)>0:
                self.telebot.sendMessage(self.creds['ids']['telegram_id'], 
                    "returned device found: {}".format(returned))
                for r in returned:
                    name = r.lower().split('-')[0].split('_')[0].replace('iphone','').replace('phone','').strip('s')
                    path = os.path.join(self.basedir, name+".wav")
                    subprocess.call(["flite","-o",path,"Proximity Warning, {0} detected. Repeat {0} has been detected ".format(name)])
                    self.castnow.cast(path, device='LIVING_ROOM')
            time.sleep(self.SLEEP)

    def __init__(self):
        BASE_DIR=os.path.dirname(os.path.abspath(__file__))
        
        logging.config.fileConfig(os.path.join(BASE_DIR,"logging.ini"))
        # get an instance of the logger object this module will use
        self.logger = logging.getLogger(__name__)
        # instantiate the JournaldLogHandler to hook into systemd
        # journald_handler = JournalHandler()
        # # set a formatter to include the level name
        # journald_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
        # # add the journald handler to the current logger
        # self.logger.addHandler(journald_handler)

        self.creds = json.loads(open(os.path.join(BASE_DIR,"my.creds"), "r").read())
        session = CookieStore(os.path.join(BASE_DIR,'session.cookie'))
        self.eero = eerolib.Eero(session)
        phone_number = self.creds['ids']['eero_phone']
        if self.eero.needs_login():
            user_token = self.eero.login(phone_number)
            verifile = os.path.join(BASE_DIR,"verifile")
            for i in range(30):
                self.logger.info("waiting on verifile!")
                if os.path.isfile(verifile):
                    self.logger.info("found!")
                    verifilefd = open(verifile, "r")
                    verification_code = verifilefd.read().strip()
                    verifilefd.close()
                    os.remove(verifile)
                    break
                else:
                    self.logger.info("not found :(")
                    time.sleep(2)
            self.eero.login_verify(verification_code, user_token)
        account = self.eero.account()
        self.network = account['networks']['data'][0]
        self.tmpdir = os.path.join(BASE_DIR,"tmp")
        self.memory = Memory(os.path.join(BASE_DIR,"memory"), self.logger)
        self.basedir = BASE_DIR
        self.telebot = telepot.Bot(self.creds["creds"]["telegram_bot_token"])
        self.castnow = CastNow(self.logger)


def main():
    detector = Detector()
    detector.detect()

if __name__ == '__main__':
    main()

