from flask import Flask, render_template, request
import json
import plotly
import time
#import pandas as pd
import numpy as np
import plotly.graph_objs as go
import os


app = Flask(__name__)
app.debug = True
statusfile = os.path.join("..","data","statusfile.txt")

def modifyline(graphid,fname,makefile=True,newfilename="",curtime=""):
    """go through the status file and turn on or off recording"""
    statout=""
    with open(fname,'r') as statfle:
        for statlne in statfle:
            #go line by line
            statsplt = statlne.strip().split(",")
            connected = statsplt[-1]
            if(int(statsplt[1])==graphid):
                if(connected=="0"):
                    raise OSError("sensor {} not connected!".format(graphid))
                #this is the right row
                if(statsplt[0]==""):
                    #in this case, the graph is not started.
                    #we pressed the start button, so we need to
                    #create a new file!
                    curtimestr = time.strftime("%Y%m%d%H%M")[2:]
                    if(curtime==""):
                        curtime = time.time()
                    if(newfilename=="" and makefile):
                        newfilename = os.path.join(".","data",curtimestr+"_odvals.csv")
                    newtimestamp = curtime
                    statout+=','.join([newfilename,\
                                str(graphid),\
                                str(newtimestamp),\
                                str(connected)])+"\n"
                else:
                    #this also happens if we are trying to delete the
                    #data file name from the status file
                    statout+=','.join([newfilename,\
                                str(graphid),\
                                "",\
                                str(connected)])+"\n"
                    #in this case, we have pressed the pause button. What happens?
                    #for now, nothing
            else:
                #for other rows, just keep going!
                #save the line
                statout+=statlne
    with open(fname,'w') as statfle2:
        statfle2.write(statout)
    return True

@app.route('/')
def index():

    graphs = [
        dict(
            data=[
                dict(
                    x=(0,),
                    y=(0,)
                )
            ],
            layout=dict(
                autosize=True,
                title='graph {}'.format(a),
                margin={'l':10,'r':10}
            )
        )
     for a in range(9)]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                           ids=ids,
                           graphJSON=graphJSON)
@app.route('/background_process_test')
def background_process_test():
    butid = request.args.get('butid')
    butsplit = butid.split('-')
    graphid = int(butsplit[-1].strip())
    if(butsplit[0]=="startbut"):
        #this means we pressed the start button.
        #so in this case we need to load the status file
        #and change the content!
        modifyline(graphid,statusfile,makefile=True)
    elif(butsplit[0]=="endbut"):
        #this is the end button, so just remove the filename
        modifyline(graphid,statusfile,makefile=False)
    return( "nothing")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
