import RPi.GPIO as GPIO
import os
import sys
import time
sys.path.append(os.path.join('.','runsensor'))
from rsens import *
from TCS34725 import TCS34725


ledpin = 7 #all the LEDs are the same pin
delay = 25 #read every 25 seconds
statuspath = os.path.join('..','data','statusfile.txt')

GPIO.setmode(GPIO.BOARD) #set the pin numbering
GPIO.setup(ledpin,GPIO.OUT,initial=GPIO.LOW)
while True:
    with open(statuspath,"r") as statfle:
        for lne in statfle:
            #each line contains: filename,i2c-address,start-time
            lsplit = lne.split(",")
            current_filename = lsplit[0]
            current_i2caddress = int(lsplit[1],16)
            current_starttime = float(lsplit[2])
            try:
                #check if the file is there!
                fle = open(current_filename,'r')
                firstline = fle.readlines()[0].split(",")
                if(firstline[0]=="time"):
                    pass
                fle.close()
            except FileNotFoundError:
                #if the file isn't there, then make it!
                initFile(current_filename)
            sensor = TCS34725(current_i2caddress)
            #senstime = time.time()-current_starttime
            data = takeReading(sensor)
            updateDict({},current_starttime,data,current_filename)
    time.sleep(delay)
