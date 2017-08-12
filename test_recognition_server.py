# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 19:16:24 2017

@author: Shaun Werkhoven
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
    
if __name__ == '__main__':
        unittest.main()