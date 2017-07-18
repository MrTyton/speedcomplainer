import os
import sys
import time
from datetime import datetime
import daemon
import signal
import threading
import multiprocessing
import twitter
import json 
import random
from logger import Logger
from optparse import OptionParser
from speedtest import Speedtest

class PingTest():
    def __init__(self, numPings=3, pingTimeout=2, maxWaitTime=6):
        self.numPings = numPings
        self.pingTimeout = pingTimeout
        self.maxWaitTime = maxWaitTime
        self.config = json.load(open('./config.json'))
        self.logger = Logger(self.config['log']['type'], { 'filename': self.config['log']['files']['ping'] })

    def run(self):
        pingResults = self.doPingTest()
        self.logPingResults(pingResults)

    def doPingTest(self):
        response = os.system("ping -c %s -W %s -w %s 8.8.8.8 > /dev/null 2>&1" % (self.numPings, (self.pingTimeout * 1000), self.maxWaitTime))
        success = 0
        if response == 0:
            success = 1
        return { 'date': datetime.now(), 'success': success }

    def logPingResults(self, pingResults):
        self.logger.log([ pingResults['date'].strftime('%Y-%m-%d'),pingResults['date'].strftime('%H:%M:%S'), str(pingResults['success'])])

class SpeedTest():
    def __init__(self):
        self.config = json.load(open('./config.json'))
        self.logger = Logger(self.config['log']['type'], { 'filename': self.config['log']['files']['speed'] })

    def run(self):
        speedTestResults = self.doSpeedTest()
        self.logSpeedTestResults(speedTestResults)
        self.tweetResults(speedTestResults)

    def doSpeedTest(self):
        # run a speed test
       
        s = Speedtest()
        try:
            s.get_best_server()
        except:
            return { 'date': datetime.now(), 'uploadResult': 0, 'downloadResult': 0, 'ping': -1 }
        
        s.download()
        s.upload()
		
        results = s.results.dict()
        pingResult = results['ping']
        downloadResult = float("{0:.2f}".format(results['download']/1e6))
        uploadResult = float("{0:.2f}".format(results['upload']/1e6))

        
        return { 'date': datetime.now(), 'uploadResult': uploadResult, 'downloadResult': downloadResult, 'ping': pingResult }

    def logSpeedTestResults(self, speedTestResults):
        self.logger.log([ speedTestResults['date'].strftime('%Y-%m-%d'),  speedTestResults['date'].strftime('%H:%M:%S'), str(speedTestResults['uploadResult']), str(speedTestResults['downloadResult']), str(speedTestResults['ping']) ])


    def tweetResults(self, speedTestResults):
        thresholdMessages = self.config['tweetThresholds']
        message = None
        for (threshold, messages) in thresholdMessages.items():
            threshold = float(threshold)
            if speedTestResults['downloadResult'] < threshold:
                message = messages[random.randint(0, len(messages) - 1)].replace('{tweetTo}', self.config['tweetTo']).replace('{internetSpeed}', self.config['internetSpeed']).replace('{downloadResult}', str(speedTestResults['downloadResult']))

        if message:
            api = twitter.Api(consumer_key=self.config['twitter']['twitterConsumerKey'],
                            consumer_secret=self.config['twitter']['twitterConsumerSecret'],
                            access_token_key=self.config['twitter']['twitterToken'],
                            access_token_secret=self.config['twitter']['twitterTokenSecret'])
            if api:
                status = api.PostUpdate(message)
                
if __name__ == "__main__":
    option_parser = OptionParser(usage="usage: %prog [flags]")
    option_parser.add_option('-p', '--ping', action='store_true', dest='ping', help='Do a ping test.')
    option_parser.add_option('-s', '--speed', action='store_true', dest='speed', help='Do a speed test')
    
    (options, args) = option_parser.parse_args()
    
    if options.ping:
        pinger = PingTest()
        pinger.run()
    if options.speed:
        speeder = SpeedTest()
        speeder.run()
                
                