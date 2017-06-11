# -*- coding: utf-8 *-*
import cv2
import numpy as np
import sys, os
#import matplotlib.pyplot as plt
import math
import time
from os import listdir
from os.path import isfile, join, basename


ANSWER_PATH = 'answer_csv/'

OPENCFU_PATH = 'colonycounter_csv/'

def countDistance(p1, p2):
    return math.sqrt(math.pow(int(p1[0])-int(p2[0]), 2) + math.pow(int(p1[1])-int(p2[1]), 2) + math.pow(int(p1[2])-int(p2[2]), 2))

def countPrecision(truePositive, falsePositive):
    return float(truePositive)/float(truePositive + falsePositive)

def countRecall(truePositive, falseNegative):
    return float(truePositive)/float(truePositive + falseNegative)

def countFmeasure(precision, recall):
    return float(2*precision*recall/(precision+recall))

def loadResult(filename):

    if not isfile(ANSWER_PATH+filename):
        return
    if not isfile(OPENCFU_PATH+"colonycounter_"+basename(filename[:-8])+".csv"):
        return

    f = open(ANSWER_PATH+filename, 'r+')
    f.readline()
    resultList = []
    for line in f:
        group, y, x = line.split(",")
        x = int(x)
        y = int(y)
        group = int(group)
#cv2.circle(img,(x,y),5,colorList[group],-1)
        resultList.append([group, y, x, False])
    f.close

    f2 = open(OPENCFU_PATH+"colonycounter_"+basename(filename[:-8])+".csv", 'r+')
    f2.readline()
    colonycounter_resultList = []
    colonycounter_count = 0
    for line in f2:
        colonycounter_count += 1
        group, y, x = line.split(",")
        x = int(float(x))
        y = int(float(y))
        group = int(group)
#cv2.circle(img,(x,y),5,colorList[group],-1)
        colonycounter_resultList.append([group, y, x, False])
    f2.close

    return resultList, colonycounter_resultList

def saveResult(resultList):
    f = open("colonycounter_result.csv", 'w+')
    f.write("FileName,TruePositive,FalsePositive,FalseNegative,Precision,Recall,F-measure,ErrorRate\n")
    for result in resultList:
        f.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % (result[0], result[1], result[2], result[3], result[4], result[5], result[6],result[7]))
    f.close

# Colony 數量上的 Error Rate
def countErrorRate(answerCount, automaticCount):
    return float(math.fabs(automaticCount-answerCount))/float(answerCount)

if __name__=="__main__":
    FinalResultList = []
    for root, dirs, files in os.walk(ANSWER_PATH):
        for filename in files:
            print basename(filename)

            answerList, colonycounter_resultList = loadResult(filename)

            print len(colonycounter_resultList)

            if answerList != None:
                # 以下三行是針對數量方面的 TP, FP, FN 初始化
                falsePositive = len(colonycounter_resultList)
                truePositive  = 0
                falseNegative = len(answerList)

            for colonycounterResult in colonycounter_resultList:
                center_y = colonycounterResult[1]
                center_x = colonycounterResult[2]
                
                if answerList != None:
                    for answerNode in answerList:
                        if answerNode[3]:
                            continue
                        distance = countDistance([answerNode[1], answerNode[2], 0], [center_y, center_x, 0])
                        if distance < 10:
                            isFound = True
                            answerNode[3] = True
                            # 以下三行是針對數量方面的 TP, FP, FN 計算
                            truePositive  += 1
                            falsePositive -= 1
                            falseNegative -= 1
                            break
                            #print answerNode[1], answerNode[2], distance
                            #print "============================================="
            if answerList != None:
                print "FileName", filename[:-4]
                print "True Positive", truePositive
                print "False Positive", falsePositive
                print "False Negative", falseNegative
                print "Precision: ", countPrecision(truePositive, falsePositive) 
                print "Recall: ", countRecall(truePositive, falseNegative)
                
                precision = countPrecision(truePositive, falsePositive)
                recall = countRecall(truePositive, falseNegative)
                fmeasure = countFmeasure(precision, recall)
                error_rate = countErrorRate(len(answerList),len(colonycounter_resultList))
                print "F-measure", countFmeasure(precision, recall)
                FinalResultList.append([filename[:-4],truePositive,falsePositive,falseNegative,precision,recall,fmeasure,error_rate])

        saveResult(FinalResultList)
