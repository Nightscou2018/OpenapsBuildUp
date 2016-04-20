# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 13:23:24 2016

@author: mstebbins
"""


'''
import urllib3
from urllib.request import urlopen

http = urllib3.PoolManager()
URL = 'https://mikestebbinscgmtest.azurewebsites.net/api/v1/treatments?count=2'
r = http.request('GET', 'https://mikestebbinscgmtest.azurewebsites.net/api/v1/treatments?count=2')

WORDS = []
for word in urlopen(URL).readlines():
    WORDS.append(word.strip().decode('ascii'))

print(WORDS)
#print(r.headers['server'])
#print('data: ' + r.data)

'''
import requests
import pprint


r = requests.get('https://mikestebbinscgmtest.azurewebsites.net/api/v1/treatments?count=2')
print(r.status_code)
print()
print()
print(r.headers['content-type'])
print()
print()
print(r.encoding)
print()
print()
print(r.text)
print()
print()
print(r.json())
print()
print()

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(r.json())