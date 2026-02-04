#! /usr/bin/env python
#coding=utf-8

"""

    2011 Boris Tatarintsev

    Class which manages local highscores i.e.
    save score table on disk, load score table from disk, etc.

"""

import urllib.parse
import urllib.request
import socket
import tools
import binascii
import time

import __main__

from hsbasic     import HSBasic


class HSRemote(HSBasic):

    #SITE_URL = "http://mysite.ru/index.html"
    SITE_URL = "http://pydotter.xost.me/index.php"

    # init network status window

    timeout = 5

    def __init__(self):
        HSBasic.__init__(self)
        self.createEmptyScoreTables()

    def getHostIP(self, hostname):
        return socket.gethostbyname(hostname)

    def getServerResponse(self, request):
        try:
            if isinstance(request, str):
                request = request.encode('utf-8')
            f = urllib.request.urlopen(HSRemote.SITE_URL, request, HSRemote.timeout)
            response = f.read()
            if isinstance(response, bytes):
                response = response.decode('utf-8', errors='replace')
            return response
        except IOError:
            raise

    def getRemoteScores(self, gameMode):
        """Requests remote score data from server """
        try:
            p = urllib.parse.urlencode({'action': 'get_scores', 'mode': gameMode})
            response = self.getServerResponse(p).rstrip(';')[:-2]
            response = list(map(lambda x: x.split(','), response.split(';')))
            if response[0] != ['']:
                for item in response:
                    item[1] = int(item[1])
                    item.append(None)
            # create scores structure
            self.buildScoreTableFromList(response, __main__.Game.getGameTypeString(gameMode))
            return response
        except IOError:
            raise

    def getUserReplayData(self, username):
        """Get replay data """
        pass

    def sendScore(self, username, score, gameMode, replayData = None):
        """Sends new highscore to server """
        try:
            self.getRemoteScores(gameMode)
            encrypted = tools.xorEncrypt(str(username) + str(score)).getvalue()
            p = urllib.parse.urlencode({'action': 'set_score', 'username': username, 'score': score, 'mode': gameMode, \
                                  'replay': tools.serialize(replayData).getvalue(), 'key': encrypted})
            response = self.getServerResponse(p)
            if response == 'cheating!': return -1                 
            return 0
        except IOError:
            raise

    def insertScore(self, tableName, playerName, score, userData = None):
        try:
            gameType = __main__.Game.getGameTypeID(tableName)
            # the webhosting is free and laggy and skips requests very often
            # here we are sending the score and then checking if it is actually has been sent            
            self.getRemoteScores(gameType)
            if self.isHighScore(tableName, score):           
                while(not self.isInsertSuccess(tableName, playerName, score)):
                    if self.sendScore(playerName, score, gameType, userData) == -1: break
                    self.getRemoteScores(gameType)
                    time.sleep(1)
                    HSRemote.timeout += 2
        except IOError:
            raise

    def loadScores(self, gameMode = 0):
        try:
            self.getRemoteScores(__main__.Game.getGameTypeID(gameMode))
        except IOError:
            raise
