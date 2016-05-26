
# coding: utf-8

# In[1]:

#get_ipython().magic(u'matplotlib inline')

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import requests
import json
import pprint
import datetime
from datetime import date

base_url = 'https://mikestebbinscgmtest.azurewebsites.net/api/v1/entries.json?'
extra_url='find[date][$lte]=1462905809000&count=1000'
url = base_url + extra_url
print (url)


# In[2]:

r = requests.get(url)

#print(r.status_code)
#print()
#print(r.headers['content-type'])
#print(r.encoding)
#print(r.text)
#print(pprint.pprint(r.json()))
#print()
print('-----------------------------------------------------------------------------------------------------------')


# In[3]:

data=json.loads(r.text)


# In[4]:

time_and_data=[]


# In[5]:

data[1]


# In[6]:

for item in data:
    try:
        properdatetime = datetime.datetime.strptime(item['dateString'], "%a %b %d %H:%M:%S PDT %Y")
        sgv = item['sgv']
        time_and_data.append((properdatetime,sgv))
    except:
        print('missed one')


# In[7]:

print(time_and_data[0:5])


# In[8]:

time_and_data[0][0]


# In[9]:

datetime.datetime.date(time_and_data[0][0])


# In[10]:

dates_and_data=[]
for item in time_and_data:
    properdate = datetime.datetime.date(item[0])
    sgv = item[1]
    dates_and_data.append((properdate,sgv))


# In[11]:

print(dates_and_data[0:5])


# In[12]:

one_date_all_bgs={}
#lists of lists, each list is a unique date and a list of BG's

for item in dates_and_data:
    date = item[0]
    one_date_all_bgs.setdefault(date,[])
    one_date_all_bgs[date].append(item[1])


# In[ ]:

one_date_all_bgs


# In[ ]:
totaldata = []

for key in one_date_all_bgs:
    print (one_date_all_bgs[key])
    plt.figure()
    plt.boxplot(np.asarray(one_date_all_bgs[key]))

for key in one_date_all_bgs:
    totaldata.append(key)
    
plt.figure()
plt.boxplot(totaldata)

# In[ ]:

## fake up some data
#spread = np.random.rand(50) * 100
#center = np.ones(25) * 50
#flier_high = np.random.rand(10) * 100 + 100
#flier_low = np.random.rand(10) * -100
#data = np.concatenate((spread, center, flier_high, flier_low), 0)
#
## basic plot
#plt.boxplot(data)


# In[ ]:



