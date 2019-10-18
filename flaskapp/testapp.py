from flask import Flask, render_template, request
import json
import plotly
import pandas as pd
import numpy as np
import plotly.graph_objs as go


app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    rng = pd.date_range('1/1/2011', periods=750, freq='H')
    ts = pd.Series(np.random.randn(len(rng)), index=rng)

    graphs = [
        dict(
            data=[
                dict(
                    x=[1, 2, 3],
                    y=[10, 20, 30],
                    type='scatter'
                ),
            ],
            layout=dict(
                title='first graph',
                margin={'l':10,'r':10}
            )
        ),

        dict(
            data=[
                dict(
                    x=[1, 3, 5],
                    y=[10, 50, 30],
                    type='bar'
                ),
            ],
            layout=dict(
                title='second graph',
                margin={'l':10,'r':10}
            )
        ),

        dict(
            data=[
                dict(
                    x=ts.index,  # Can use the pandas data structures directly
                    y=ts
                )
            ],
            layout=dict(
                title='third graph',
                margin={'l':10,'r':10}
            )
        )
    ]*3

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
