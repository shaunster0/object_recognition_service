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


### test String
### curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://imgdirect.s3-website-us-west-2.amazonaws.com/neither.jpg"}' http://127.0.0.1:5000/img/api/v1.0/images
@app.route('/img/api/v1.0/images', methods = ['POST'])
#@auth.login_required
def add_imgs():
    if not request.json:
        abort(400)
        
    missing_url = False
    json_str = request.json
    img_data = json_str['new_imgs']
    new_images = []
    
    for img in img_data:
        if img.get('url') == None:
            missing_url = True
            continue
        
        if img.get('title') == None:
            new_title = ""
        else:
            new_title = img.get('title')
        if img.get('results') == None:
            new_results = ""
        else:
            new_results = img.get('results')
            
        image = {
            # simple way to ensure a unique id
            'id' : images[-1]['id'] + 1,
            'title': new_title,
            # url is required, otherwise return error
            'url': img['url'],
            'results': new_results,
            'resize': False,
            'size': ""
        }
        images.append(image)
        new_images.append(image)
        
    if missing_url:
        return_val = jsonify(new_images), 410
    else:
        return_val = jsonify(new_images), 201
    
    return return_val


### test String
### curl -i -H "Content-Type: application/json" -X DELETE http://127.0.0.1:5000/img/api/v1.0/images/3
@app.route('/img/api/v1.0/images/<int:img_id>', methods=['DELETE'])
#@auth.login_required
def delete_img(img_id):
    img = [img for img in images if img['id'] == img_id]
    if len(img) == 0:
        abort(404)
    images.remove(img[0])
    return jsonify({'result': True})


def main(_):
    app.run(host = '0.0.0.0')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
  # classify_image_graph_def.pb:
  #   Binary representation of the GraphDef protocol buffer.
  # imagenet_synset_to_human_label_map.txt:
  #   Map from synset ID to a human readable string.
  # imagenet_2012_challenge_label_map_proto.pbtxt:
  #   Text representation of a protocol buffer mapping a label to synset ID.
    parser.add_argument(
      '--model_dir',
      type = str,
      default = '/tmp/imagenet',
      help = """\
      Path to classify_image_graph_def.pb,
      imagenet_synset_to_human_label_map.txt, and
      imagenet_2012_challenge_label_map_proto.pbtxt.\
      """
  )
    parser.add_argument(
      '--image_file',
      type = str,
      default = '',
      help = 'Absolute path to image file.'
  )
    parser.add_argument(
      '--num_top_predictions',
      type = int,
      default = 5,
      help = 'Display this many predictions.'
  )
    FLAGS, unparsed = parser.parse_known_args()
    tf.app.run(main = main, argv = [sys.argv[0]] + unparsed)
    