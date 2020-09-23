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
prevtime = time.time()
datapath = os.path.join('..','data')
statuspath = os.path.join(datapath,'statusfile.txt')
readnow = 0
debug = 0

GPIO.setmode(GPIO.BOARD) #set the pin numbering
GPIO.setup(ledpin,GPIO.OUT,initial=GPIO.LOW)
while True:
    statuslist = {}
    curtime = time.time()-prevtime
    if(curtime > delay):
        readnow = 1
        prevtime = time.time()
    else:
        readnow = 0
    try:
        with open(statuspath,"r") as statfle:
            if(debug):
                print("foundfile!")
            #go through the file to pull in the status
            #of each sensor
            for lne in statfle:
                lsplit = lne.strip().split(",")
                current_filename = lsplit[0]
                current_i2caddress = int(lsplit[1])
                if(lsplit[2]==""):
                    current_starttime =0.0
                else:
                    current_starttime = float(lsplit[2])
                current_connected = int(lsplit[3])
                statuslist[current_i2caddress] = \
                        (current_filename,current_starttime,current_connected)
    except IOError:
        if(debug):
            print("nofile!")
        #if the statusfile doesn't exist, then make it
        with open(statuspath,"w") as statfle:
            statfle.write('\n'.join([","+a+",,0" for a in range(8)]))
    outtxt=""
    for current_i2caddress in range(8):
        if(debug):
            print("currently on "+str(current_i2caddress))
        #this will iterate through 8 possible multiplexer positions.

        tomeasure = []
        lastsensor = None
        multiplexer = TCA9548A()
        nomult = False
        try:
            sensorstatus = statuslist[current_i2caddress]
            if(debug):
                print("us!")
        except KeyError:
            if(debug):
                print("no status, set it to zero")
            #if we can't find the current sensor in the list then assume we
            #know nothing about it or someone mangled the file
            sensorstatus = ('',0.0,0)
        current_filename = sensorstatus[0]
        #current_i2caddress = int(lsplit[1])
        current_starttime = sensorstatus[1]
        current_connected = sensorstatus[2]
        if(current_filename==""):
            if(debug):
                print("don't record data")
            #if there's no filename, that means don't record anything.
            pass
        else:
            #otherwise, check to see if the file is there
            try:
                #check if the data file is there!
                fle = open(os.path.join(datapath,current_filename),'r')
                firstline = fle.readlines()[0].split(",")
                if(firstline[0]=="time"):
                    pass
                fle.close()
            except OSError:
                #if the file isn't there, then make it!
                initFile(os.path.join(datapath,current_filename))
        try:
            multiplexer.tcaselect(current_i2caddress)
            if(debug):
                print("found multiplexer")
        except OSError:
            if(debug):
                print("multiplexer not present")
            #this part makes it so the program thinks
            #there is only one data window if the multiplexer
            #is not present. Otherwise, every data window
            #would be showing the same data!
            if(current_i2caddress==0):
                current_connected = 1
            else:
                current_connected = 0
            #this happens if the multiplexer isn't plugged in
            #just keep trying until it works
            #in this case we could still be good, since
            #we can still have one sensor plugged in
            nomult = True
        try:
            sensor = TCS34725()
            lastsensor = sensor
            if(debug):
                print("found sensor")
            if(not nomult):
                #so, if we have a multiplexer, and we detected
                #a sensor, then write that down! otherwise, we already
                #wrote down that we have only one sensor, above
                current_connected = 1
        except OSError:
            if(debug):
                print("didn't find sensor")
            #this happens if the sensor isn't connected
            if(not nomult):
                #so, if we have a multiplexer, and we detected
                #there is no sensor, then write that down!
                current_connected = 0
                current_filename = ""
                current_starttime = ""

        outputline = ','.join([str(current_filename),\
                            str(current_i2caddress),\
                            str(current_starttime),\
                            str(current_connected)])+"\n"
        outtxt+= outputline
        if(current_connected and not (current_filename == "")):
            #if we're connected and we have a filename, then record!
            tomeasure+=[[current_filename,\
                current_i2caddress,\
                current_starttime,None]]
        if(len(tomeasure)>0 and readnow):
            #only do this stuff if there's something to measure
            GPIO.output(ledpin,GPIO.HIGH) #LED on
            time.sleep(1.4)
            for sensor in tomeasure:
                #take light measurements for everything
                if(not nomult):
                    multiplexer.tcaselect(sensor[1])
                data = takeBGReading(lastsensor)
                sensor[3] = data
            GPIO.output(ledpin,GPIO.LOW) #LED off
            time.sleep(1.4)
            for sensor in tomeasure:
                #take dark measurements for everything
                if(not nomult):
                    multiplexer.tcaselect(sensor[1])
                lum_ctrl = takeBGReading(lastsensor)
                sensor[3]['ctrl_r'] = lum_ctrl['r']
                sensor[3]['ctrl_g'] = lum_ctrl['g']
                sensor[3]['ctrl_b'] = lum_ctrl['b']
                sensor[3]['ctrl_c'] = lum_ctrl['c']
                #now, save everything
                updateDict({},sensor[2],sensor[3],os.path.join(datapath,sensor[0]))
    with open(statuspath,"w") as statfle:
        statfle.write(outtxt)
    time.sleep(1)
