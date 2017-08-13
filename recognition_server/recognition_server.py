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
try:
    from recognition_server import tf_operations
except:
    import tf_operations


# set up HTTP app
auth = HTTPBasicAuth()
app = Flask(__name__)

# initialise image list with some random images, not strictly necessary
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

# set up some error handlers
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


# first API function, can be used for testing
@app.route('/')
@app.route('/index')
def index():
    """returns Hello, World!"""
    return "Hello, World!"
    

# test string
# curl -i http://127.0.0.1:5000/img/api/v1.0/images
@app.route('/img/api/v1.0/images', methods=['GET'])
#@auth.login_required
def get_imgs():
    """
    returns in JSON format all the images currently stored by the server. 
    Includes all fields, such as ID, and URL
    """
    return jsonify({'images': images})


# test String
# curl -i http://127.0.0.1:5000/img/api/v1.0/images/2
@app.route('/img/api/v1.0/images/<int:img_id>', methods = ['GET'])
#@auth.login_required
def get_img(img_id):
    """
    returns in JSON format a specific image currently stored by the server.
    Requires the image ID to be included in the HTTP address
    """
    img = [img for img in images if img['id'] == img_id]
    if len(img) == 0:
        abort(404)
    return jsonify({'img': img[0]})


# test String
# curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://imgdirect.s3-website-us-west-2.amazonaws.com/neither.jpg"}' http://127.0.0.1:5000/img/api/v1.0/images
@app.route('/img/api/v1.0/images', methods = ['POST'])
#@auth.login_required
def add_imgs():
    """
    adds images to the server image list. The images must be provided as a list 
    encoded with JSON and sent with the HTTP post. A URL is required. Inference 
    is not automatically run on them.
    """
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
        # add new image records to image list
        images.append(image)
        new_images.append(image)
        
    if missing_url:
        return_val = jsonify(new_images), 410
    else:
        return_val = jsonify(new_images), 201
    
    return return_val


# test string
# curl -X PUT -i -H "Content-Type: application/json" -d '{ \"id\": \"1\"}' http://127.0.0.1:5000/img/api/v1.0/infer/1
@app.route('/img/api/v1.0/infer/<int:img_id>', methods = ['PUT'])
#@auth.login_required
def infer(img_id):
    """
    runs TensorFlow inference (recognition) on an image which is already in the images 
    list. The image ID must be included in the HTTP address and encoded with JSON.
    Results are returned in JSON
    """
    img = [img for img in images if img['id'] == img_id]
    if len(img) == 0:
        abort(404)
    if not request.json:
        abort(400)
        
    url = img[0]['url']
    # call TensorFlow
    img[0]['results'] = tf_operations.run_inference_on_image(url)
    return jsonify({'img': img[0]}), 200


# test string
# curl -X PUT -i http://127.0.0.1:5000/img/api/v1.0/inferundone
# calls TensorFlow, so can be slow if many images are undone
@app.route('/img/api/v1.0/inferundone', methods = ['PUT'])
#@auth.login_required
def infer_undone():
    """
    runs TensorFlow inference (recognition) on all images which are in the images 
    list but for which inference has not already been run. Results are returned in JSON
    """
    undone_imgs = [img for img in images if img['results'] == '']
    if len(undone_imgs) == 0:
        abort(404)
    
    for img in undone_imgs:
        # call TensorFlow
        img['results'] = tf_operations.run_inference_on_image(img['url'])
        
    return jsonify({'images': undone_imgs}), 200


# test String
# curl -i -H "Content-Type: application/json" -X POST -d '{"url":"http://imgdirect.s3-website-us-west-2.amazonaws.com/neither.jpg"}' http://127.0.0.1:5000/img/api/v1.0/imagesinfer
# another TensorFlow function, again can be slow if many images are added
@app.route('/img/api/v1.0/imagesinfer', methods = ['POST'])
#@auth.login_required
def add_imgs_infer():
    """
    adds new images to the image list and runs TensorFlow inference (recognition) 
    on them. New images must be provided with a URL, and given in JSON format. 
    Results are returned in JSON format.
    """
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
        # call TensorFlow
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


# test String
# curl -i -H "Content-Type: application/json" -X DELETE http://127.0.0.1:5000/img/api/v1.0/images/3
@app.route('/img/api/v1.0/images/<int:img_id>', methods=['DELETE'])
#@auth.login_required
def delete_img(img_id):
    """
    deletes an image from the server image list. The image ID must be given in the HTTP
    address
    """
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
    