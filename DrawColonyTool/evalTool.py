#!/usr/bin/python
import sys
import time
import cv2
import numpy as np
from soundEffect import sound
from os.path import basename, isfile

mode = True # if True, draw rectangle. Press 'm' to toggle to curve
group = 0
resultList = []
colorList = [(255,0,0), 
             (0,255,0),
             (0,0,255),
             (255,255,0),
             (255,0,255),
             (0,255,255),
             (128,255,255),
             (255,128,128),
             (255,255,128),
             (128,128,128)]

radius = 6
SoundPlayer = None

# mouse callback function
def draw_circle(event,x,y,flags,param):
    global mode,group, resultList

    if event == cv2.EVENT_LBUTTONDOWN:
        #drawing = True
        if (len(resultList) % 10) != 0:
            SoundPlayer.coin()
        else:
            SoundPlayer.up()
        cv2.circle(img,(x - radius/2,y - radius/2),radius,colorList[group],-1)
        resultList.append([group, y, x])
    elif event == cv2.EVENT_MOUSEMOVE:
        '''
        if drawing == True:
            if mode == True:
                cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
            else:
                cv2.circle(img,(x,y),5,(0,0,255),-1)
        '''
    elif event == cv2.EVENT_LBUTTONUP:
        '''
        drawing = False
        if ix == x and iy == y:
            if (len(resultList) % 10) != 0:
                SoundPlayer.coin()
            else:
                SoundPlayer.up()
            cv2.circle(img,(x - radius/2,y - radius/2),radius,colorList[group],-1)
            resultList.append([group, y, x])
        
        if mode == True:
            cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
        else:
            cv2.circle(img,(x,y),5,(0,0,255),-1)
        '''

def loadResult(filename):
    if not isfile(filename+".csv"):
        return
    f = open(filename+".csv", 'r+')
    f.readline()
    for line in f:
        group, y, x = line.split(",")
        x = int(x)
        y = int(y)
        group = int(group)
        cv2.circle(img,(x - radius/2,y - radius/2),radius,colorList[group],-1)
        resultList.append([group, y, x])
    f.close

def saveResult(filename):
    f = open(filename+".csv", 'w+')
    f.write("Group,Y,X\n")
    for result in resultList:
        f.write("%s,%s,%s\n" % (result[0], result[1], result[2]))

if __name__ == '__main__':
    filePath = sys.argv[1]
    fileName = basename(filePath)
    #SoundPlayer = sound.Player()
    SoundPlayer = sound.Player("PeterWolf - SoundEffect", 0.001)
    SoundPlayer.start()
    img = cv2.imread(filePath)
    loadResult(fileName)
    cv2.namedWindow(fileName)
    cv2.setMouseCallback(fileName,draw_circle)
    while(1):        
        cv2.imshow(fileName,img)
        k = cv2.waitKey(1) & 0xFF
        #print k
        if k == ord('m'):
            SoundPlayer.jump()
            mode = not mode
        elif k == 27:  #esc
            SoundPlayer.loseLife()
            SoundPlayer.stop()
            break
        elif k == ord('u'): #u
            if len(resultList) == 0:
                continue
            resultList.pop()
            img = cv2.imread(filePath)
            for result in resultList:              
                group, y, x = result
                cv2.circle(img,(x - radius/2,y - radius/2),radius,colorList[group],-1)

        elif k >= 48 and k <= 57: # 0~9
            SoundPlayer.powerUp()
            group = k - 48
            
        time.sleep(0.05)
        
    SoundPlayer.join()
    saveResult(fileName)
    cv2.destroyAllWindows()
