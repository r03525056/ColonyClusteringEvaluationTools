#!/usr/bin/env python
# -*- coding:utf-8 -*-
import time
import os
# import platform
from threading import Thread

class Player(Thread):
    def __init__(self, string, sleeptime):
        Thread.__init__(self)
        self.wavDir = os.path.dirname(os.path.abspath(__file__))
        self.sleepTime = sleeptime
        # if "Linux" in platform.platform():
        #     self.cmd = "play"
        # elif "Windows" in playform.platform():
        #     self.cmd = "start"
        # else:
            # self.cmd = "afplay"
        self.cmd = "afplay"
        
        self.isPlay = False
        self.soundList = []
        self.isStop = False
    
    def run(self):
        while not self.isStop:
            if len(self.soundList) > 0:
                os.system("{0} {1}/{2}".format(self.cmd, self.wavDir, self.soundList.pop()))
            time.sleep(self.sleepTime)
    
    def up(self):
        self.soundList.append("smb3_sound_effects_1_up.wav")
        
    def coin(self):
        self.soundList.append("smb3_sound_effects_coin.wav")
        
    def jump(self):
        self.soundList.append("smb3_sound_effects_jump.wav")
        
    def loseLife(self):
        self.soundList.append("smb3_sound_effects_lost_life.wav")
        
    def powerUp(self):
        self.soundList.append("smb3_sound_effects_power_up.wav")
        
    def stop(self):
        time.sleep(1)
        self.isStop = True
        
if __name__ == "__main__":
    p = Player()
    p.start()
    p.up()
    p.coin()