# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from dynamic_orchestrator.models.inline_response200 import InlineResponse200  # noqa: E501
from dynamic_orchestrator.test import BaseTestCase
from pathlib import Path
from nt import getcwd

class TestAppModelController(BaseTestCase):
    """AppModelController integration test stubs"""

    def test_appmodel_create(self):
        """Test case for appmodel_create

        
        """    
        data = dict(app_id = 'app_id_example', 
                    file = (open('ProvaMonitorModel.yml', 'rb'),'ProvaMonitorModel.yml','text/plain'))
        
        response = self.client.open(
            '/orchestrator/appmodel',
            method='POST',
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                      'Response body is : ' + response.data.decode('utf-8'))

    def test_appmodel_read_all(self):
        """Test case for appmodel_read_all

        
        """
        response = self.client.open(
            '/orchestrator/appmodel',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_appmodel_update(self):
        """Test case for appmodel_update

        
        """
        data = dict(body=(open('ProvaMonitorModel.yml', 'rb'),'ProvaMonitorModel.yml','text/plain'))   
        response = self.client.open(
            '/orchestrator/appmodel/{app_id}'.format(app_id='app_id_example'),
            method='PUT',
            data=data,
            content_type='text/plain')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
