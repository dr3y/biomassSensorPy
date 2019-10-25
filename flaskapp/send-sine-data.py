import numpy as np
import json
import time
import asyncio
import websockets
import os

_GOODBYE_MESSAGE = u'Goodbye'

x = np.arange(0,np.pi*10,0.1).tolist()
y = np.sin(x).tolist()
data_size = len(x)
counter = 0
graph_size = 100

samples = 0
tic = time.time()

def get_graph_data(fname):
    #print("statusfile is "+fname)
    global counter,data_size,graph_size,x,y
    global samples,tic
    curtime = time.time()
    chanlist = []
    with open(fname,'r') as statusfile:
        channelslist = {}
        for line in statusfile:
            lspl = [ a.strip() for a in line.split(',')]

            channame = int(lspl[1]) #which channel is it? 0-6
            chanlist+=[channame]
            chanfile = lspl[0] #filename. Can be empty
            connected = int(lspl[3]) #is this channel connected? 1 or 0
            startbut = 0
            endbut = 0
            visible = True
            #possibile scenarios:
            if(connected):
                #print("channel "+str(channame)+" is connected")
                if(chanfile==''):
                    #in this case we are connected but havent started
                    #recording
                    startbut = 0 #this means "start" is available
                    endbut = 1 #this means "end" is not shown
                    x=(0)
                    y=(0)
                else:
                    #in this case we have been recording
                    startbut = 1 #this means start is in "pause"
                    endbut = 0 #end is enabled
                    x = []
                    y = []
                    if(chanfile[0]=="."):
                        chanfile = "."+chanfile
                    try:
                        #the file may not be created yet
                        with open(chanfile, 'r') as datafile:
                            for dataline in datafile:
                                if('time' in dataline):
                                    continue
                                datasplit = dataline.split(",")
                                newx = float(datasplit[0])
                                newy = float(datasplit[4])-float(datasplit[8])
                                x+=[newx]
                                y+=[newy]
                    except FileNotFoundError:
                        #it's ok, just wait until it is created!
                        print("data file does not exist!")
                        #raise Warning("data file does not exist!")
                    x = tuple(x)
                    y = tuple(y)
            else:
                #this means we are not connected
                visible = False
                startbut = 2 #this means startbut is not visible
                endbut = 1 #this means endbut is not visible
            channelslist[str(channame)] = {"data":{"x":x,"y":y},\
                                    "buttons":{"start":startbut,"end":endbut},\
                                    "visible":visible}
    channelslist["channels"]=[str(a) for a in chanlist]
    return json.dumps(channelslist)
    #Calculate FPS
    '''
    samples += 1
    if (time.time() - tic) > 2:
        print("FPS is : "+str(samples /(time.time() - tic)))
        samples = 0
        tic = time.time()

    counter += 1
    if counter > (data_size - graph_size):
        counter = 0

    graph_to_send = json.dumps({
        'x':x[counter:counter+graph_size],
        'y':y[counter:counter+graph_size]
    })
    return graph_to_send
    #'''
#print(get_graph_data(os.path.join("..","data","statusfile.txt")))
async def hello(websocket,path):
    while True:
        await websocket.send(get_graph_data(os.path.join("..","data","statusfile.txt")))
        await asyncio.sleep(1)
    #async with websockets.connect(uri) as websocket:
    #    await websocket.send(get_graph_data())
        #await websocket.recv()

asyncio.get_event_loop().run_until_complete(
    websockets.serve(hello,'127.0.0.1',9997))

asyncio.get_event_loop().run_forever()
