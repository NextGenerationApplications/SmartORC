# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server.test import BaseTestCase


class TestAppModelController(BaseTestCase):
    """AppModelController integration test stubs"""

    def test_appmodel_create(self):
        """Test case for appmodel_create

        
        """
        data = dict(app_id='app_id_example',
                    file='file_example')
        response = self.client.open(
            '/appmodel',
            method='POST',
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_appmodel_read_all(self):
        """Test case for appmodel_read_all

        
        """
        response = self.client.open(
            '/appmodel',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_appmodel_update(self):
        """Test case for appmodel_update

        
        """
        body = Object()
        response = self.client.open(
            '/appmodel/{AppID}'.format(app_id='app_id_example'),
            method='PUT',
            data=json.dumps(body),
            content_type='application/octet-stream; charset=utf-8')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
