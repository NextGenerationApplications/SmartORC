# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from dynamic_orchestrator.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_appmodel_delete(self):
        """Test case for appmodel_delete

        
        """
        response = self.client.open(
            '/orchestrator/appmodel/app_id_example',
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_depplan_create(self):
        """Test case for depplan_create

        
        """
        query_string = [('app_id', 'app_id_example'),
                        ('federation_id', 'federation_id_example')]
        response = self.client.open(
            '/orchestrator/depplan/',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_monitordata_delete(self):
        """Test case for monitordata_delete

        
        """
        response = self.client.open(
            '/orchestrator/monitordata/{FederationID}'.format(federation_id='federation_id_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
