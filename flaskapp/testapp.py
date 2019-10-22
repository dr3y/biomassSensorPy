from flask import Flask, render_template, request
import json
import plotly
#import pandas as pd
import numpy as np
import plotly.graph_objs as go


app = Flask(__name__)
app.debug = True


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
    print(butid)
    #if request.method == 'POST':
    #    print(request)
    return( "nothing")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
