# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 18:08:52 2017

@author: Shaun Werkhoven
@purpose: To create a image classification system for the Image Intelligence 
TakeHome Assignment

Licensed under the Apache License, Version 2.0 (the "License");

Simple image classification with flask-based HTTP API, TensorFlow 
and the Inception model (trained on ImageNet 2012 Challenge data
set).

The server maintains a list of images, with URLs, on which image inference can 
be run, or has been run. It is a list of tasks to do, or that 
have been done. Functions to add, delete or run inference on images are given
as HTTP addresses, using JSON arguments.

This program creates a graph from a saved GraphDef protocol buffer,
and runs inference on an input JPEG, GIF or PNG image. It outputs human readable
strings of the top 5 predictions along with their probabilities.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import json
from flask import Flask, jsonify, abort, make_response, request
from flask_httpauth import HTTPBasicAuth
import tf_operations

auth = HTTPBasicAuth()
app = Flask(__name__)

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


### test string
### curl -X PUT -i -H "Content-Type: application/json" -d '{ \"id\": \"1\"}' http://127.0.0.1:5000/img/api/v1.0/infer/1
@app.route('/img/api/v1.0/infer/<int:img_id>', methods = ['PUT'])
#@auth.login_required
def infer(img_id):
    img = [img for img in images if img['id'] == img_id]
    if len(img) == 0:
        abort(404)
    if not request.json:
        abort(400)
        
    url = img[0]['url']
    img[0]['results'] = tf_operations.run_inference_on_image(url)
    return jsonify({'img': img[0]}), 200


### test string
### curl -X PUT -i http://127.0.0.1:5000/img/api/v1.0/inferundone
@app.route('/img/api/v1.0/inferundone', methods = ['PUT'])
#@auth.login_required
def infer_undone():
    undone_imgs = [img for img in images if img['results'] == '']
    if len(undone_imgs) == 0:
        abort(404)
    
    for img in undone_imgs:
        img['results'] = tf_operations.run_inference_on_image(img['url'])
        
    return jsonify({'images': undone_imgs}), 200


### test String
### curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://imgdirect.s3-website-us-west-2.amazonaws.com/neither.jpg"}' http://127.0.0.1:5000/img/api/v1.0/imagesinfer
@app.route('/img/api/v1.0/imagesinfer', methods = ['POST'])
#@auth.login_required
def add_imgs_infer():
    
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
        new_results = tf_operations.run_inference_on_image(img['url'])
        
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
    tf_operations.parse_args()
    tf_operations.download_and_extract_model_if_needed()
    app.run(host = '0.0.0.0')


if __name__ == '__main__':
    tf_operations.tf.app.run(main = main, argv = [sys.argv[0]])
    