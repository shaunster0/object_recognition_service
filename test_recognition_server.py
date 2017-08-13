# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 19:16:24 2017

@author: Shaun Werkhoven
@purpose: run unit tests for recognition_server.py
"""

import pytest
import os
import recognition_server
import unittest
import json


class Recognition_ServerTestCase(unittest.TestCase):
    def setUp(self):
        recognition_server.app.config['TESTING'] = True
        self.app = recognition_server.app.test_client()
        recognition_server.parse_args()
     
    def tearDown(self):
        pass

    def test_get_imgs(self):
        """Check that root exists"""
        rv = self.app.get('/img/api/v1.0/images')
        self.assertEqual(rv.status_code, 200)
        assert b'images' in rv.data
      
    def test_non_existing_function(self):
        """Check that 404 gets thrown for a function that doesn't exist"""
        rv = self.app.get('/img/api/v1.0/a-bad-address')
        self.assertEqual(rv.status_code, 404)
        
    def test_get_individual_image(self):
        """Check that an image exists"""
        rv = self.app.get('/img/api/v1.0/images/2')
        #headers=headers)
        self.assertEqual(rv.status_code, 200)    
    
    def test_get_non_existing_individual_image(self):
        """Check that 404 gets thrown for an image address that doesn't exist"""
        rv = self.app.get('/img/api/v1.0/images/crazy-non-existing')
        self.assertEqual(rv.status_code, 404)   
    
    def test_create_new_images(self):
        """create a new image file using JSON and POST"""
        new_im1 = dict(url = 'http://imgdirect.s3-website-us-west-2.amazonaws.com/neither1.jpg')
        new_im2 = dict(url = 'http://imgdirect.s3-website-us-west-2.amazonaws.com/neither2.jpg')
        rv=self.app.post('/img/api/v1.0/images',
           data=json.dumps(dict(new_imgs = [new_im1, new_im2])),
           content_type = 'application/json')
        self.assertEqual(rv.status_code, 201)
        self.assertIn(b'neither1.jpg', rv.data)
        self.assertIn(b'neither2.jpg', rv.data)
    
    def test_create_not_json_new_image(self):
        """attempt to create an image without JSON"""
        rv=self.app.post('/img/api/v1.0/images',
           data = '[http://imgdirect.s3-website-us-west-2.amazonaws.com/neither.jpg]',
           content_type = 'application/json')
        self.assertEqual(rv.status_code, 400)
    
    def test_delete_existing_image(self):
        """Does a record get deleted correctly"""
        rv=self.app.delete('/img/api/v1.0/images/3',
           content_type = 'application/json')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'true',rv.data)
        
    def test_put_inference_on_image(self):
        """Use PUT to run inference on an image"""
        rv=self.app.put('/img/api/v1.0/infer/1',
           data = json.dumps(dict(id = 1)),
           content_type = 'application/json')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'0.5944', rv.data)
    
    def test_add_and_inference_on_image(self):
        """Use POST to run inference and add image"""
        new_im = {"url": "https://farm4.static.flickr.com/3118/3275588806_33384d2638.jpg"}
        newims = dict(new_imgs = [new_im])
        rv=self.app.post('/img/api/v1.0/imagesinfer',
           data = json.dumps(newims),
           content_type = 'application/json')
        self.assertEqual(rv.status_code, 201)
        self.assertIn(b'0.1822', rv.data)
    
if __name__ == '__main__':
        unittest.main()