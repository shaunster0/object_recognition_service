# -*- coding: utf-8 -*-
"""
Created on Sat Aug 12 19:16:24 2017

@author: Shaun Werkhoven
"""

import pytest
import os
import tempfile
import recognition_server
import unittest
import json
import requests
from base64 import b64encode


class Recognition_ServerTestCase(unittest.TestCase):
    def setUp(self):
        recognition_server.app.config['TESTING'] = True
        self.app = recognition_server.app.test_client()
        
    
if __name__ == '__main__':
        unittest.main()