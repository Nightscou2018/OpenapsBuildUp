import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import datetime
from datetime import date
import time
from plotly.offline import plot
#import plotly.plotly as py
import plotly.graph_objs as go
#from plotly.graph_objs import Scatter
#from plotly.graph_objs import *
#import pprint
#import matplotlib

from_date='04/01/2016'
to_date='05/25/2016'

def datestring_to_epoch_str(input_string):
    return str(int(time.mktime(datetime.datetime.strptime(input_string, "%m/%d/%Y").timetuple())))+'000'

from_date_epoch = datestring_to_epoch_str(from_date)
to_date_epoch = datestring_to_epoch_str(to_date)

base_url = 'https://mikestebbinscgmtest.azurewebsites.net/api/v1/entries.json?'
extra_url='find[date][$gte]='+from_date_epoch+'&find[date][$lt]='+to_date_epoch+'&count=10000'
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

#one_date_all_bgs

totaldata = []

#for key in one_date_all_bgs:
#    print (one_date_all_bgs[key])
#    plt.figure()
#    plt.boxplot(np.asarray(one_date_all_bgs[key]))

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
    title='BGs',
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
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    margin=dict(
        l=40,
        r=30,
        b=80,
        t=100,
    ),
    paper_bgcolor='rgb(243, 243, 243)',
    plot_bgcolor='rgb(243, 243, 243)',
#    width=1200,
#    height=800,
    showlegend=False,
)

fig = go.Figure(data=traces, layout=layout)
plot_url = plot(fig, filename='BGs.html')

# Combine all values from list of lists into one list and display it
all_bgs = [j for i in y_data for j in i]
#plot([Box(y = all_bgs,showlegend=False)], show_link=True)

bgs_before=[]
bgs_after=[]

for key in sorted(one_date_all_bgs.keys()):
    print(key)   
    if key < datetime.date(2016, 5, 1):
        bgs_before.append(one_date_all_bgs[key])
    else:
        bgs_after.append(one_date_all_bgs[key])

traces=[]
traces.append (go.Box(
    x=0,    
    y=bgs_before,
    boxpoints='all',
    jitter=0.5,
    whiskerwidth=0.2,
    marker=dict(
    size=2,
    ),
    line=dict(width=1),
))

traces.append (go.Box(
    x=1,
    y=bgs_after,
    boxpoints='all',
    jitter=0.5,
    whiskerwidth=0.2,
    marker=dict(
    size=2,
    ),
    line=dict(width=1),
))

layout = go.Layout(
    title='BGs',
    xaxis=dict(
        autorange=True,
        showgrid=False,
        zeroline=False,
        ),
    yaxis=dict(
        autorange=True,
        showgrid=True,
        zeroline=True,
        dtick=50,
        gridcolor='rgb(255, 255, 255)',
        gridwidth=1,
        zerolinecolor='rgb(255, 255, 255)',
        zerolinewidth=2,
    ),
    showlegend=False,
)

fig = go.Figure(data=traces, layout=layout)
plot_url = plot(data, filename='before & after')

#traces=[]
#for yd in zip(all_bgs):
#        traces.append(go.Box(
#            y=yd,
#            boxpoints='all',
#            jitter=0.5,
#            whiskerwidth=0.2,
#            marker=dict(
#                size=2,
#            ),
#            line=dict(width=1),
#        ))  
#        
#layout = go.Layout(
#    title='BGs',
#    xaxis=dict(
#        autorange=True,
#        showgrid=False,
#        zeroline=False,
#        tickangle=270
#        ),
#    yaxis=dict(
#        autorange=False,
#        showgrid=True,
#        zeroline=True,
#        dtick=50,
#        gridcolor='rgb(255, 255, 255)',
#        gridwidth=1,
#        zerolinecolor='rgb(255, 255, 255)',
#        zerolinewidth=2,
#    ),
#    margin=dict(
#        l=40,
#        r=30,
#        b=80,
#        t=100,
#    ),
#    paper_bgcolor='rgb(243, 243, 243)',
#    plot_bgcolor='rgb(243, 243, 243)',
##    width=1200,
##    height=800,
#    showlegend=False,
#)
#
#fig = go.Figure(data=traces, layout=layout)
#plot_url = plot(fig, filename='BGs.html')
