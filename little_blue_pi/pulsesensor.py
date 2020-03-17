# extended from https://github.com/WorldFamousElectronics/PulseSensor_Amped_Arduino

import time
import threading
import RPi.GPIO as GPIO
import smbus
bus = smbus.SMBus(1)

class ADC:
    address = None

    REG_ADDR_RESULT = 0x00
    REG_ADDR_ALERT  = 0x01
    REG_ADDR_CONFIG = 0x02
    REG_ADDR_LIMITL = 0x03
    REG_ADDR_LIMITH = 0x04
    REG_ADDR_HYST   = 0x05
    REG_ADDR_CONVL  = 0x06
    REG_ADDR_CONVH  = 0x07

    def __init__(self,address=0x55):
        self.address=address
        bus.write_byte_data(self.address, self.REG_ADDR_CONFIG,0x20)

    def adc_read(self):
        data=bus.read_i2c_block_data(self.address, self.REG_ADDR_RESULT, 2)
        raw_val=(data[0]&0x0f)<<8 | data[1]
        return raw_val


class Pulsesensor:
    def __init__(self, channel = 0, bus = 0, device = 0):
        self.channel = channel
        self.BPM = 0
        self.adc = ADC(address=0x50)
        # init variables
        self.rate = [0] * 10         # array to hold last 10 IBI values
        self.sampleCounter = 0       # used to determine pulse timing
        self.lastBeatTime = 0        # used to find IBI
        self.P = 512                 # used to find peak in pulse wave, seeded
        self.T = 512                 # used to find trough in pulse wave, seeded
        self.thresh = 525            # used to find instant moment of heart beat, seeded
        self.amp = 100               # used to hold amplitude of pulse waveform, seeded
        self.firstBeat = True        # used to seed rate array so we startup with reasonable BPM
        self.secondBeat = False      # used to seed rate array so we startup with reasonable BPM

        self.N = 0

        self.IBI = 600               # int that holds the time interval between beats! Must be seeded!
        self.Pulse = False           # "True" when User's live heartbeat is detected. "False" when not a "live beat". 
        self.lastTime = int(time.time()*1000)

    def getBPMLoop(self):
        
        
        #while not self.thread.stopped:
            Signal = self.adc.adc_read()
            currentTime = int(time.time()*1000)
            
            self.sampleCounter += currentTime - self.lastTime
            self.lastTime = currentTime
            
            self.N = self.sampleCounter - self.lastBeatTime

            # find the peak and trough of the pulse wave
            if Signal < self.thresh and self.N > (self.IBI/5.0)*3:     # avoid dichrotic noise by waiting 3/5 of last IBI
                if Signal < self.T:                          # T is the trough
                    self.T = Signal                          # keep track of lowest point in pulse wave 

            if Signal > self.thresh and Signal > self.P:
                self.P = Signal

            # signal surges up in value every time there is a pulse
            if self.N > 250:                                 # avoid high frequency noise
                if Signal > self.thresh and self.Pulse == False and self.N > (self.IBI/5.0)*3:       
                    self.Pulse = True                        # set the Pulse flag when we think there is a pulse
                    self.IBI = self.sampleCounter - self.lastBeatTime  # measure time between beats in mS
                    self.lastBeatTime = self.sampleCounter        # keep track of time for next pulse

                    if self.secondBeat:                      # if this is the second beat, if secondBeat == TRUE
                        self.secondBeat = False             # clear secondBeat flag
                        for i in range(len(self.rate)):      # seed the running total to get a realisitic BPM at startup
                          self.rate[i] = self.IBI

                    if self.firstBeat:                       # if it's the first time we found a beat, if firstBeat == TRUE
                        self.firstBeat = False              # clear firstBeat flag
                        self.secondBeat = True              # set the second beat flag
                        

                    # keep a running total of the last 10 IBI values  
                    self.rate[:-1] = self.rate[1:]                # shift data in the rate array
                    self.rate[-1] = self.IBI                      # add the latest IBI to the rate array
                    runningTotal = sum(self.rate)            # add upp oldest IBI values

                    runningTotal /= len(self.rate)           # average the IBI values 
                    self.BPM = 60000/runningTotal       # how many beats can fit into a minute? that's BPM!

            if Signal < self.thresh and self.Pulse == True:       # when the values are going down, the beat is over
                self.Pulse = False                           # reset the Pulse flag so we can do it again
                self.amp = self.P - self.T                             # get amplitude of the pulse wave
                self.thresh = self.amp/2 + self.T                      # set thresh at 50% of the amplitude
                self.P = self.thresh                              # reset these for next time
                self.T = self.thresh

            if self.N > 2500:                                # if 2.5 seconds go by without a beat
                self.thresh = 512                            # set thresh default
                self.P = 512                                 # set P default
                self.T = 512                                 # set T default
                self.lastBeatTime = self.sampleCounter            # bring the lastBeatTime up to date        
                self.firstBeat = True                        # set these to avoid noise
                self.secondBeat = False                      # when we get the heartbeat back
                self.BPM = 0

            #time.sleep(0.005)
            
        
    # # Start getBPMLoop routine which saves the BPM in its variable
    # def startAsyncBPM(self):
    #     self.thread = threading.Thread(target=self.getBPMLoop)
    #     self.thread.stopped = False
    #     self.thread.start()
    #     return
        
    # # Stop the routine
    # def stopAsyncBPM(self):
    #     self.thread.stopped = True
    #     self.BPM = 0
    #     return
