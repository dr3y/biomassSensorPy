import RPi.GPIO as GPIO
import os
import sys
import time
sys.path.append(os.path.join('.','runsensor'))
from rsens import *
from TCS34725 import TCS34725
from TCA9548A import TCA9548A


ledpin = 7 #all the LEDs are the same pin
delay = 25 #read every 25 seconds
datapath = os.path.join('..','data')
statuspath = os.path.join(datapath,'statusfile.txt')

GPIO.setmode(GPIO.BOARD) #set the pin numbering
GPIO.setup(ledpin,GPIO.OUT,initial=GPIO.LOW)
while True:
    with open(statuspath,"r") as statfle:

        tomeasure = []
        lastsensor = None
        multiplexer = TCA9548A()
        for lne in statfle:
            #each line contains: filename,i2c-address,start-time
            lsplit = lne.split(",")
            current_filename = lsplit[0]
            current_i2caddress = int(lsplit[1])
            current_starttime = float(lsplit[2])
            tomeasure+=[[current_filename,current_i2caddress,current_starttime,None]]
            try:
                #check if the file is there!
                fle = open(os.path.join(datapath,current_filename),'r')
                firstline = fle.readlines()[0].split(",")
                if(firstline[0]=="time"):
                    pass
                fle.close()
            except FileNotFoundError:
                #if the file isn't there, then make it!
                initFile(os.path.join(datapath,current_filename))
            multiplexer.tcaselect(current_i2caddress)
            sensor = TCS34725()
            lastsensor = sensor
        GPIO.output(ledpin,GPIO.HIGH) #LED on
        time.sleep(1.4)
        for sensor in tomeasure:
            #take light measurements for everything
            multiplexer.tcaselect(sensor[1])
            data = takeBGReading(lastsensor)
            sensor[3] = data
        GPIO.output(ledpin,GPIO.LOW) #LED off
        time.sleep(1.4)
        for sensor in tomeasure:
            #take dark measurements for everything
            multiplexer.tcaselect(sensor[1])
            lum_ctrl = takeBGReading(lastsensor)
            sensor[3]['ctrl_r'] = lum_ctrl['r']
            sensor[3]['ctrl_g'] = lum_ctrl['g']
            sensor[3]['ctrl_b'] = lum_ctrl['b']
            sensor[3]['ctrl_c'] = lum_ctrl['c']
            #now, save everything
            updateDict({},sensor[2],sensor[3],os.path.join(datapath,sensor[0]))
    time.sleep(delay)
