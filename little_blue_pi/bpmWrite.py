from pulsesensor import Pulsesensor
from datetime import datetime
import threading
import csv
import os
import time
import numpy as np
import sys

annotation = ''

def generateTimestamp():
    now = datetime.now()
    timeStamp = str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'_'+str(now.day)+'-'+str(now.month)+'-'+str(now.year)
    print(timeStamp)
    return timeStamp

def writeFile(fullPath):
    o = open(fullPath, 'w')
    writer = csv.writer(o)
    writer.writerow(['TimeStamp','BPM','Annotation'])

def appendToFile(fullPath, ts, BPM, anno):
    data = [ts, BPM, anno]
    o = open(fullPath, 'a')
    writer = csv.writer(o)
    writer.writerow(data)
    
def signal_user_input():
    while True:
        global annotation
        annotation = sys.stdin.readline()




ts = generateTimestamp()
basePath = '/home/pi/bluetooth_pi_2-master/little_blue_pi/files'
pathName = basePath+'/'+ts

os.mkdir(pathName)

baseFileName = ts
fileName = baseFileName
fullPath = pathName+'/'+fileName+'.csv'
writeFile(fullPath)

lines = ''

p = Pulsesensor()
# p.startAsyncBPM()

threading.Thread(target=signal_user_input).start()

try:
    while True:
        p.getBPMLoop()
        bpm = p.BPM
        dataTS = generateTimestamp()
        if os.path.getsize(fullPath)>39990000:
            fileName = generateTimestamp()
            fullPath = pathName+'/'+fileName+'.csv'
            writeFile(fullPath)
        appendToFile(fullPath, dataTS, bpm, annotation)
        annotation = ''
        time.sleep(1)
except:
    threading.Thread(target=signal_user_input).stopped = True