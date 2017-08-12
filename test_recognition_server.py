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
    
if __name__ == '__main__':
        unittest.main()