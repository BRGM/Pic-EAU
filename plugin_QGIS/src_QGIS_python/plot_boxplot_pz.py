# coding=utf-8

import os
#from .hubeau import getWLDataFromPoint
import pandas as pd
import plotly
#import plotly.plotly as py
import plotly.graph_objs as go
from pandas.io.json import json_normalize
import webbrowser

def BoxPlotStat_Descr(data='current_wl_ts.json', trace='Y', bx_out_html='cur_ts_box_plot.html'):
    #current_wl_ts
    # box plot: pas vu comment spécifier les Q1,Q2,Q3,etc.qui figurent dans ce fichier stat_descr.json
    # lire le json avec les données dedans
    df=pd.read_json(data, orient='table')
    df_data=df['data']

    c=[]
    for item in df_data:
        c.append(item)
    df_data = json_normalize(c)
    #afficher un graph plotly
    li_bss=pd.unique(df_data['code_bss'])
    trace0=go.Box(y=df_data['niveau_nappe_eau'],name = str(li_bss), marker = dict(color = 'rgb(0, 128, 128)',))
    data = [trace0]
    title=str('Piézomètre :'+li_bss)
    if trace=='Y':
        cur_box_plot_html=plotly.offline.plot({"data": data, "layout":go.Layout(title=title)}, link_text=None, auto_open=True, filename='cur_ts_boxplot.html', output_type='div')
        plot=plotly.offline.plot({"data": data, "layout": go.Layout(title=title)}, link_text=None, auto_open=True,
                        filename='cur_ts_box_plot.html', output_type='file')
        return cur_box_plot_html, plotly.offline.plot({"data": data, "layout": go.Layout(title=title)}, link_text=None, auto_open=True,
                        filename='cur_ts_box_plot.html', output_type='file'),\
           webbrowser.open('file://' + os.path.realpath('cur_ts_box_plot.html'))
    else:
        plotly.offline.plot({"data": data, "layout": go.Layout(title=title)}, link_text=None, auto_open=False,
                        filename=bx_out_html, output_type='file')
        pass

if __name__=="__main__":
    BoxPlotStat_Descr()