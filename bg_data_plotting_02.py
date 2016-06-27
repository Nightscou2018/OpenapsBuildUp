# Pull BG values from Nightscout API and plot offline box-whisker plots
# references:
#   https://plot.ly/python/axes/
#   https://plot.ly/python/static-image-export/
#   https://plot.ly/python/reference/#box-x0
#   https://plot.ly/python/box-plots/
#   https://plot.ly/python/violin-plot/
#   https://plot.ly/python/offline/   

import requests
import json
import datetime
from datetime import date
import time
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.plotly as py
#import numpy as np
#import matplotlib.pyplot as plt
#import plotly.plotly as py
#from plotly.graph_objs import Scatter
#from plotly.graph_objs import *
#import pprint
#import matplotlib

from_date='04/01/2016'
to_date='06/01/2016'

def datestring_to_epoch_str(input_string):
    return str(int(time.mktime(datetime.datetime.strptime(input_string, "%m/%d/%Y").timetuple())))+'000'

from_date_epoch = datestring_to_epoch_str(from_date)
to_date_epoch = datestring_to_epoch_str(to_date)

base_url = 'https://mikestebbinscgmtest.azurewebsites.net/api/v1/entries.json?'
extra_url='find[date][$gte]='+from_date_epoch+'&find[date][$lt]='+to_date_epoch+'&count=50000'
url = base_url + extra_url
print (url)

r = requests.get(url)

#print(r.status_code)
#print()
#print(r.headers['content-type'])
#print(r.encoding)
#print(r.text)
#print(pprint.pprint(r.json()))
#print()
print('-----------------------------------------------------------------------------------------------------------')

data=json.loads(r.text)
time_and_data=[]
data[1]

for item in data:
    try:
        properdatetime = datetime.datetime.strptime(item['dateString'], "%a %b %d %H:%M:%S PDT %Y")
        sgv = item['sgv']
        if sgv < 30 or sgv > 500:
            print('bad sgv value')
        else:
            time_and_data.append((properdatetime,sgv))
    except:
        print('type = ',item['type'])

#time_and_data[0][0]

datetime.datetime.date(time_and_data[0][0])

dates_and_data=[]
for item in time_and_data:
    properdate = datetime.datetime.date(item[0])
    sgv = item[1]
    dates_and_data.append((properdate,sgv))

#print(dates_and_data[0:5])

one_date_all_bgs={}
#lists of lists, each list is a unique date and a list of BG's

for item in dates_and_data:
    date = item[0]
    one_date_all_bgs.setdefault(date,[])
    one_date_all_bgs[date].append(item[1])

totaldata = []

for key in one_date_all_bgs:
    totaldata.append(key)
     
# # examples from plotly website for offline graph
# plot([Scatter(x=[1, 2, 3], y=[3, 1, 6])])
# plot([Box(y = np.random.randn(50), showlegend=False) for i in range(45)], show_link=True)

list_of_lists_of_bgs_only=[]
list_of_dates=[]

for key in sorted(one_date_all_bgs.keys()):
    print(key)   
    list_of_dates.append(datetime.datetime.strftime(key,'%m-%d-%Y'))
    list_of_lists_of_bgs_only.append(one_date_all_bgs[key])
    
#plot([Box(y = list_of_lists_of_bgs_only[i],showlegend=False) for i in range(len(list_of_lists_of_bgs_only))], show_link=True)

#------------------------------------------------------------------------------------------------
# Plot all days individually

x_data = list_of_dates
y_data = list_of_lists_of_bgs_only
x_pos = list(range(1,len(x_data)))
          
traces=[]

for xd, yd, xpos in zip(x_data, y_data, x_pos):
        traces.append(go.Box(
            x=xpos,
            y=yd,
            name=xd,
            boxpoints='all',
            jitter=0.5,
            whiskerwidth=0.2,
            marker=dict(
                size=2,
            ),
            line=dict(width=1),
        ))  
        
layout = go.Layout(
    title='blood glucose values before and after 5-1-16 implementation',
    xaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        tickangle=270
        ),
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=50,
        gridcolor='rgb(220, 220, 220)',
        gridwidth=1,
        zerolinecolor='rgb(220, 220, 220)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
#    paper_bgcolor='rgb(243, 243, 243)',
#    plot_bgcolor='rgb(243, 243, 243)',
    width=1920,
    height=1080,
    showlegend=False,
)

fig = go.Figure(data=traces, layout=layout)
plot_url = plot(fig, filename='BGs.html')

#------------------------------------------------------------------------------------------------
# Plot aggregate Before and After closed-loop

# Combine all values from list of lists into one list and display it
all_bgs = [j for i in y_data for j in i]
#plot([Box(y = all_bgs,showlegend=False)], show_link=True)

bgs_before=[]
bgs_after=[]

for key in sorted(one_date_all_bgs.keys()):
    print(key)   
    for value in one_date_all_bgs[key]:
        if key < datetime.date(2016, 5, 1):
            bgs_before.append(value)
        else:
            bgs_after.append(value)
            
bgs_after_outliers_removed=[]
for each in bgs_after:
    if each < 250 and each > 60:
        bgs_after_outliers_removed.append(each)

caption_temp_before = '<b>BEFORE</b>'+'<br>'+'(4/01 - 4/30)'
caption_temp_after = '<b>AFTER</b>'+'<br>'+'(5/01 - 5/31)'
            
x_data = [caption_temp_before,caption_temp_after,'<b>legend</b>']
x_pos = [0,10,17]

trace0 = (go.Box(
    x=x_pos[0],    
    y=bgs_before,
    name=x_data[0],
#    boxmean='sd',
    boxpoints='all',
    jitter=0.5,
    whiskerwidth=0.2,
    marker=dict(
    size=2,
    ),
    line=dict(width=1),
))

trace1 = (go.Box(
    x=x_pos[1],  
    y=bgs_after,
    name=x_data[1],
#    boxmean='sd',
    boxpoints='all',    
    jitter=0.5,
    whiskerwidth=0.2,
    marker=dict(
    size=2,
    ),
    line=dict(width=1),
))


trace2 = (go.Box(
    x=x_pos[2],  
    y=bgs_after_outliers_removed,
    name=x_data[2],
#    boxmean='sd',
    boxpoints=False,
#    visible=False,
    jitter=0.5,
    whiskerwidth=0.2,
   #fillcolor='rgb(0,0,0)',
    marker=dict(
    size=2,
    color='rgb(0,0,0)',
    ),
    line=dict(
    color='rgb(0,0,0)',
    width=1)
    )
)

layouttheone = go.Layout(
    title='aggregate blood glucose values <b>BEFORE</b> and <b>AFTER</b> OpenAPS implementation',
    width=1600,
    height=900,
    showlegend=False,    
    xaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        titlefont=dict(
            size=32)
            ),
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=50,
        gridcolor='rgb(220, 220, 220)',
        gridwidth=1,
        zerolinecolor='rgb(220, 220, 220)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    )
)

data0=[trace0,trace1,trace2]

fig = go.Figure(data=data0, layout=layouttheone)
plot_url = plot(fig, filename='before_&_after.html')


#-----------------------------------------------------------------------------
# Play around with histograms

trace0 = go.Histogram(
    x=bgs_before,
    opacity=0.75
)
trace1 = go.Histogram(
    x=bgs_after,
    opacity=0.75
)
data = [trace0, trace1]
layout = go.Layout(
    barmode='overlay'
)
fig = go.Figure(data=data, layout=layout)
plot_url = plot(fig, filename='overlaid-histogram')

# make a smoothed line plot/area chart

d={}
for k,v in zip([int(i*10) for i in bgs_before],bgs_before):
   d.setdefault(k,[]).append(v)

LoL=[d[e] for e in sorted(d.keys(), reverse=True)]

x_before = []
y_before = []

for i,l in enumerate(LoL,1):
    print('list',i,l) 
    x_before.append(l[0])
    y_before.append(len(l))
    
d={}
for k,v in zip([int(i*10) for i in bgs_after],bgs_after):
   d.setdefault(k,[]).append(v)

LoL=[d[e] for e in sorted(d.keys(), reverse=True)]

x_after = []
y_after = []

for i,l in enumerate(LoL,1):
    print('list',i,l) 
    x_after.append(l[0])
    y_after.append(len(l))

trace0 = go.Scatter(
    x=x_before,
    y=y_before,
    mode='lines+markers',
    name="'spline'",
    text=["tweak line smoothness<br>with 'smoothing' in line object"],
    hoverinfo='text+name',
    line=dict(
        shape='spline'
    )
)

trace1 = go.Scatter(
    x=x_after,
    y=y_after,
    mode='lines+markers',
    name="'spline'",
    text=["tweak line smoothness<br>with 'smoothing' in line object"],
    hoverinfo='text+name',
    line=dict(
        shape='spline'
    )
)

data = [trace0,trace1]
layout = dict(
    legend=dict(
        y=0.5,
        traceorder='reversed',
        font=dict(
            size=16
        )
    )
)
fig = go.Figure(data=data, layout=layout)
plot_url = plot(fig, filename='smooth-line')