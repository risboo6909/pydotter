#! /usr/bin/env python
#coding=utf-8

"""

    2011 Boris Tatarintsev

    Class which manages local highscores i.e.
    save score table on disk, load score table from disk, etc.

"""

import os
import pickle
from io import BytesIO

from hsbasic import HSBasic

class HSLocal(HSBasic):

    SCORE_FILENAME = os.path.join('..', 'highscores')
    
    def __init__(self):
        HSBasic.__init__(self)

    def dumpScoresData(self):
        stream = BytesIO()
        pickle.dump(self.getScoreTables(), stream, pickle.HIGHEST_PROTOCOL)
        return stream

    def loadScoreData(self):
        data = []
        try:
            f = open(HSLocal.SCORE_FILENAME, 'rb')
            data = f.read()
            f.close()
        except IOError:
            # error reading file, try to create a new empty
            # high scores data file
            self.createEmptyScoreTables()
            stream = self.dumpScoresData()
            f = open(HSLocal.SCORE_FILENAME, 'wb')
            f.write(stream.getvalue())
            f.close()                
        return data

    def loadScores(self, gameMode = 0):
        data = self.loadScoreData()
        # deserialize fetched data
        if data:
            self.setScoreTables(pickle.loads(data))

    def insertScore(self, tableName, playerName, score, userData = None):
        HSBasic.insertScore(self, tableName, playerName, score, userData)

    def saveScoreData(self):
        data = self.dumpScoresData()
        f = open(HSLocal.SCORE_FILENAME, 'wb')
        f.write(data.getvalue())
        f.close()
