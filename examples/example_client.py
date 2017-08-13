# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 21:31:04 2017

@author: Shaun Werkhoven
"""

# requires recognition_server.py to be running
# provides some simple examples of using the service

import requests
import json


res = requests.put('http://127.0.0.1:5000/img/api/v1.0/infer/1', json = dict(id = 1))
if res.ok:
    parsed = res.json()
    print(json.dumps(parsed, indent = 4, sort_keys = True))
        
        
newim1 = dict(url = 'http://imgdirect.s3-website-us-west-2.amazonaws.com/neither.jpg')
newim2 = dict(url = 'http://imgdirect.s3-website-us-west-2.amazonaws.com/neither2.jpg')
newims = dict(new_imgs = [newim1, newim2])
res1 = requests.post('http://127.0.0.1:5000/img/api/v1.0/images', json = newims)
if res1.ok:
    parsed = res1.json()
    print(json.dumps(parsed, indent = 4, sort_keys = True))


res2 = requests.put('http://127.0.0.1:5000/img/api/v1.0/inferundone')
if res2.ok:
    parsed = res2.json()
    print(json.dumps(parsed, indent = 4, sort_keys = True))


new_im = {"url": "https://farm4.static.flickr.com/3118/3275588806_33384d2638.jpg"}
newims = dict(new_imgs = [new_im])
res3 = requests.post('http://127.0.0.1:5000/img/api/v1.0/imagesinfer', json = newims)
if res3.ok:
    parsed = res3.json()
    print(json.dumps(parsed, indent = 4, sort_keys = True))
    
    
res4 = requests.delete('http://127.0.0.1:5000/img/api/v1.0/images/1')
if res4.ok:
    parsed = res.json()
    print(json.dumps(parsed, indent = 4, sort_keys = True))
        