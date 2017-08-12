# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 18:08:52 2017

@author: Shaun Werkhoven
@purpose: To create a image classification system for the Image Intelligence 
TakeHome Assignment

Licensed under the Apache License, Version 2.0 (the "License");

Simple image classification with TensorFlow and the Inception model.

Run image classification with Inception trained on ImageNet 2012 Challenge data
set.

This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG, GIF or PNG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import os.path
import re
import sys
import tarfile

import numpy as np
import tensorflow as tf

import json
import urllib
from flask import Flask, jsonify, render_template, abort, make_response, request, Markup
from flask_httpauth import HTTPBasicAuth
from PIL import Image

auth = HTTPBasicAuth()
app = Flask(__name__)

FLAGS = None

DATA_URL = 'http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz'

images = [
    {
        'id': 1,
        'title': u'Nikes',
        'url': 'http://imgdirect.s3-website-us-west-2.amazonaws.com/nike.jpg',
        'results': '',
        'resize': False,
        'size': ""
    },
    {
        'id': 2,
        'title': u'Altra',
        'url': 'https://s3-us-west-2.amazonaws.com/imgdirect/altra.jpg',
        'results': '',
        'resize': False,
        'size': ""
    }
]

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'unauthorized access'}), 403)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'missing json data'}), 400)


@app.errorhandler(410)
def missing_URL(error):
    return make_response(jsonify({'error': 'missing URL field'}), 410)


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
    

### test string
### curl -i http://127.0.0.1:5000/img/api/v1.0/images
@app.route('/img/api/v1.0/images', methods=['GET'])
#@auth.login_required
def get_imgs():
    return jsonify({'images': images})


### test String
### curl -i http://127.0.0.1:5000/img/api/v1.0/images/2
@app.route('/img/api/v1.0/images/<int:img_id>', methods = ['GET'])
#@auth.login_required
def get_img(img_id):
    img = [img for img in images if img['id'] == img_id]
    if len(img) == 0:
        abort(404)
    return jsonify({'img': img[0]})
