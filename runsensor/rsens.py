import time
from TCS34725 import TCS34725
import RPi.GPIO as GPIO
import numpy as np
import matplotlib.pyplot as plt



ledpin = 7

def initSensor():
    """initialize the sensor and setup the gpio"""
    GPIO.setmode(GPIO.BOARD) #set the pin numbering
    GPIO.setup(ledpin,GPIO.OUT,initial=GPIO.LOW) #set the pin to output
    return TCS34725() #intialize the i2c comm
def takeReading(sensor):
    GPIO.output(ledpin,GPIO.HIGH) #LED on
    time.sleep(1.4) #wait for the integration time of the sensor
    lum = sensor.readluminance() #read the sensor
    GPIO.output(ledpin,GPIO.LOW) #LED off
    time.sleep(1.4) #wait for integration time
    lum_ctrl = sensor.readluminance() #read the sensor; background control
    lum['ctrl_r'] = lum_ctrl['r']
    lum['ctrl_g'] = lum_ctrl['g']
    lum['ctrl_b'] = lum_ctrl['b']
    lum['ctrl_c'] = lum_ctrl['c']
    return lum
def updateDict(indict,starttime,newdict,outfname = None):
    """adds the current reading to the existing dictionary; also
    to the file if desired"""
    curtime = time.time()-starttime
    if(type(outfname)==str):
        fstr = ','.join([str(a) for a in [curtime,\
                        newdict['r'],newdict['g'],\
                        newdict['b'],newdict['c'],\
                        newdict['ctrl_r'],newdict['ctrl_g'],\
                        newdict['ctrl_b'],newdict['ctrl_c']]])+"\n"
        with open(outfname,"a") as outfleline:
                    outfleline.writelines(fstr)
    for key in indict:
        if(key=='time'):
            continue
        else:
            indict[key] = indict[key] + [newdict[key]]
    indict['time']= indict['time']+[curtime]
def initFile(outfname):
    """start the file which will save the output"""
    outfle = open(outfname,"w")
    outfle.write("time,R,G,B,C,ctrlR,ctrlG,ctrlB,ctrlC\n")
    outfle.close()
def initplot():
    """initialize the interactive plot"""
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.ion()
    fig.show()
    fig.canvas.draw()
    return fig,ax
def readFile(fname):
    """reads a file and converts it into a dictionary, sort of like a dataframe"""
    vdict = []
    with open(outfname,"r") as outfle:
        columns = []
        for fline in outfle:
            sfline = fline.split(",")
            if(vdict==[]):
                columns = sfline
                for value in sfline:
                    vdict[value]=[]
            else:
                for value,datum in zip(sfline,columns):
                    vdict[value]=[datum]
    return vdict
def updatePlot(fig,ax,valsdict):
    """update the interactive plot. run every time you take a new reading!"""
    #ax = fig.ax
    ax.clear()
    ax.plot(valsdict['time'], \
            [a[0]-a[1] for a in zip(valsdict['r'],valsdict['ctrl_r'])],\
            color='red')
    ax.plot(valsdict['time'], \
            [a[0]-a[1] for a in zip(valsdict['g'],valsdict['ctrl_g'])],\
            color='green')
    ax.plot(valsdict['time'], \
            [a[0]-a[1] for a in zip(valsdict['b'],valsdict['ctrl_b'])],\
            color='blue')
    ax.plot(valsdict['time'], \
            [a[0]-a[1] for a in zip(valsdict['c'],valsdict['ctrl_c'])],\
            color='black')
    fig.canvas.draw()
