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


class NodeLookup(object):
  """Converts integer node ID's to human readable labels."""

  def __init__(self,
               label_lookup_path=None,
               uid_lookup_path=None):
    if not label_lookup_path:
      label_lookup_path = os.path.join(
          FLAGS.model_dir, 'imagenet_2012_challenge_label_map_proto.pbtxt')
    if not uid_lookup_path:
      uid_lookup_path = os.path.join(
          FLAGS.model_dir, 'imagenet_synset_to_human_label_map.txt')
    self.node_lookup = self.load(label_lookup_path, uid_lookup_path)
    
  def load(self, label_lookup_path, uid_lookup_path):
    """Loads a human readable English name for each softmax node.

    Args:
      label_lookup_path: string UID to integer node ID.
      uid_lookup_path: string UID to human-readable string.

    Returns:
      dict from integer node ID to human-readable string.
    """
    if not tf.gfile.Exists(uid_lookup_path):
      tf.logging.fatal('File does not exist %s', uid_lookup_path)
    if not tf.gfile.Exists(label_lookup_path):
      tf.logging.fatal('File does not exist %s', label_lookup_path)

    # Loads mapping from string UID to human-readable string
    proto_as_ascii_lines = tf.gfile.GFile(uid_lookup_path).readlines()
    uid_to_human = {}
    p = re.compile(r'[n\d]*[ \S,]*')
    for line in proto_as_ascii_lines:
      parsed_items = p.findall(line)
      uid = parsed_items[0]
      human_string = parsed_items[2]
      uid_to_human[uid] = human_string
    
       # Loads mapping from string UID to integer node ID.
    node_id_to_uid = {}
    proto_as_ascii = tf.gfile.GFile(label_lookup_path).readlines()
    for line in proto_as_ascii:
      if line.startswith('  target_class:'):
        target_class = int(line.split(': ')[1])
      if line.startswith('  target_class_string:'):
        target_class_string = line.split(': ')[1]
        node_id_to_uid[target_class] = target_class_string[1:-2]

    # Loads the final mapping of integer node ID to human-readable string
    node_id_to_name = {}
    for key, val in node_id_to_uid.items():
      if val not in uid_to_human:
        tf.logging.fatal('Failed to locate: %s', val)
      name = uid_to_human[val]
      node_id_to_name[key] = name

    return node_id_to_name
              

def download_and_extract_model_if_needed():
  """Download and extract model tar file."""
  dest_directory = FLAGS.model_dir
  if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)
  filename = DATA_URL.split('/')[-1]
  filepath = os.path.join(dest_directory, filename)
  if not os.path.exists(filepath):
    def _progress(count, block_size, total_size):
      sys.stdout.write('\r>> Downloading %s %.1f%%' % (
          filename, float(count * block_size) / float(total_size) * 100.0))
      sys.stdout.flush()
    filepath, _ = urllib.request.urlretrieve(DATA_URL, filepath, _progress)
    print()
    statinfo = os.stat(filepath)
    print('Successfully downloaded', filename, statinfo.st_size, 'bytes.')
  tarfile.open(filepath, 'r:gz').extractall(dest_directory)


def main(_):
    download_and_extract_model_if_needed()
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
    