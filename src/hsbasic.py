#! /usr/bin/env python
#coding=utf-8

"""

    2011 Boris Tatarintsev
    
    Base class for high-score managers.
    Any specific high-score manager must derive from this class
    and implement its methods.

"""

import pickle
import copy
import strings

class HSBasic(object):
    
    SORT_ASC = 0
    SORT_DESC = 1
    SORT_NOSORT = 2

    SCORES_COUNT = 25

    
    def __init__(self):
        self.__mScoreTables = { }
        self.__mLastScoreIdx = { }
        
    def __sortTable(self, table, sort_type):
        rev = False
        if sort_type == HSBasic.SORT_NOSORT: return
        if sort_type == HSBasic.SORT_DESC: rev = True
        return sorted(table, key = lambda x: x[1], reverse = rev)

    def createEmptyScoreTables(self):
        self.addNewScoreTable(strings.STR_MAIN_MENU_STANDART, capacity = HSBasic.SCORES_COUNT)
        self.addNewScoreTable(strings.STR_MAIN_MENU_SURVIVE, capacity = HSBasic.SCORES_COUNT)
        
    def addNewScoreTable(self, tableName, capacity = -1):
        # we can have as many score tables as we want
        self.__mScoreTables[tableName] = \
            { \
                'sort': HSBasic.SORT_DESC, \
                'capacity': capacity, \
                'scores': [] \
            }
    
    def removeScoreTable(self, tableName):
        del self.__mScoreTables[tableName]

    def buildScoreTableFromList(self, scoreList, tableName):
        if scoreList[0] != ['']:
            stype = self.__mScoreTables[tableName]['sort']
            self.__mScoreTables[tableName]['scores'] = self.__sortTable(scoreList, stype)

    def isHighScore(self, tableName, score):
        # checks if score is big enough to be inserted in score table        
        table = self.__mScoreTables[tableName]['scores']
        stype = self.__mScoreTables[tableName]['sort']
        capacity = self.__mScoreTables[tableName]['capacity']
        # the procedure is not very efficient but we don't need
        # to perform insertion too often, so it's ok ;)
        tmp_table = copy.deepcopy(table)
        tmp_table.append( [ None, score ] )        
        tmp_table = self.__sortTable(tmp_table, stype)        
        # get the slice
        if capacity != -1:
            table = tmp_table[:capacity]
        else:
            table = tmp_table[:]        
        if [ None, score ] not in table:            
            return False
        return True

    def isInsertSuccess(self, tableName, playerName, score):
        # checks if score is big enough to be inserted in score table        
        table = self.__mScoreTables[tableName]['scores']
        stype = self.__mScoreTables[tableName]['sort']
        capacity = self.__mScoreTables[tableName]['capacity']
        # the procedure is not very efficient but we don't need
        # to perform insertion too often, so it's ok ;)
        tmp_table = copy.deepcopy(table)
        tmp_table = self.__sortTable(tmp_table, stype)        
        # get the slice
        if capacity != -1:
            table = tmp_table[:capacity]
        else:
            table = tmp_table[:]
        # cut replay data
        for idx in range(len(table)):
            item = table[idx]
            table[idx] = item[:2]
        if [ playerName, score ] not in table:            
            return False
        return True

    def insertScore(self, tableName, playerName, score, userData = None):
        # inserts new score into selected table
        if self.isHighScore(tableName, score):
            table = self.__mScoreTables[tableName]['scores']
            stype = self.__mScoreTables[tableName]['sort']
            capacity = self.__mScoreTables[tableName]['capacity']
            # the procedure is not very efficient but we don't need
            # to do insertion often, so it's ok ;)
            table = [ [ playerName, score, userData ] ] + table
            table = self.__sortTable(table, stype)
            # find the last item in the sorted scoretable
            self.__mLastScoreIdx[tableName] = table.index([ playerName, score, userData ])
            self.__mScoreTables[tableName]['scores'] = table

    def getScoreIter(self, tableName):        
        return iter(self.__mScoreTables[tableName]['scores'])

    def getLastScoreIdx(self, tableName):
        if tableName in self.__mLastScoreIdx:            
            return self.__mLastScoreIdx[tableName]
        else:
            return -1

    def getScoreTables(self):
        return self.__mScoreTables
    
    def getScoreByIdx(self, tableName, idx):
        return self.__mScoreTables[tableName]['scores'][idx]
        
    def setSortOrder(self, tableName, value):
        if value == SORT_ASC or value == SORT_DESC or value == SORT_NOSORT:
            self.__mScoreTables[tableName]['sort'] = value            
            self.__sortTable(self.__mScoreTables[tableName]['scores'], value)

    def setScoreTables(self, scoreTables):
        self.__mScoreTables = scoreTables
