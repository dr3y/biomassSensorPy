import time

import numpy as np
import json
import asyncio
import websockets

_GOODBYE_MESSAGE = u'Goodbye'

x = np.arange(0,np.pi*10,0.1).tolist()
y = np.sin(x).tolist()
data_size = len(x)
counter = 0
graph_size = 100

samples = 0
tic = time.time()

def get_graph_data():

    global counter,data_size,graph_size,x,y
    global samples,tic

    #Calculate FPS
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

async def hello(websocket,path):
    while True:
        await websocket.send(get_graph_data())
        await asyncio.sleep(.2)
    #async with websockets.connect(uri) as websocket:
    #    await websocket.send(get_graph_data())
        #await websocket.recv()

asyncio.get_event_loop().run_until_complete(
    websockets.serve(hello,'127.0.0.1',9997))

asyncio.get_event_loop().run_forever()
