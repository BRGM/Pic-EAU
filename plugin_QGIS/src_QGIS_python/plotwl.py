# coding=utf-8

import os
#from .hubeau import getWLDataFromPoint
import pandas as pd
import plotly
#import plotly.plotly as py
import plotly.graph_objs as go
from pandas.io.json import json_normalize
import webbrowser

def plotWaterLevel(data='current_wl_ts.json', trace='Y', out_html='cur_wl_ts.html'):
    # lire le json avec les données dedans
    df=pd.read_json(data, orient='table')
    df_data=df['data']

    c=[]
    for item in df_data:
        c.append(item)
    df_data = json_normalize(c)
    #afficher un graph plotly
    data = [go.Scatter(x=df_data['date_mesure'],y=df_data['niveau_nappe_eau'])]
    li_bss=pd.unique(df_data['code_bss'])
    title=str('Piézomètre :'+li_bss)
    if trace == 'Y':
        cur_ts_plot_html=plotly.offline.plot({"data": data, "layout":go.Layout(title=title)}, link_text=None, auto_open=True, filename='cur_wl_ts.html', output_type='div')
        return cur_ts_plot_html, webbrowser.open('file://' + os.path.realpath('cur_wl_ts.html'))
    else :
        pl=plotly.offline.plot({"data": data, "layout": go.Layout(title=title)}, link_text=None, auto_open=False,
                        filename=out_html, output_type='file')
        return pl
        #plotly.offline.plot({"data": data, "layout": go.Layout(title=title)}, link_text=None, auto_open=True,filename='cur_wl_ts.html', output_type='file'),\

if __name__=="__main__":
    plotWaterLevel()
