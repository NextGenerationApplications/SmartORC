
from __future__ import absolute_import

from flask import json
from dynamic_orchestrator.test import BaseTestCase
import os

test_file_federation_id = 'MonitorDataFileID1'
test_file_name = 'MonitorModel.yml'
test_file_path = './'

update_test_file_federation_id = 'MonitorDataFileID1'
update_test_file_name = 'MonitorModel2.yml'
update_test_file_path = './'
 
class TestMonitorDataController(BaseTestCase):
    """MonitorDataController integration test stubs"""

    def test_monitordata_create(self):
        """Test case for monitordata_create
   
        """
        data = dict(app_id = self.test_file_federation_id, 
                    file = (open(os.path.join(self.test_file_path, self.test_file_name), 'rb'), self.test_file_name, 'text/plain'))

        response = self.client.open(
            '/orchestrator/monitordata',
            method='POST',
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_monitordata_read_all(self):
        """Test case for monitordata_read_all

        
        """
        response = self.client.open(
            '/orchestrator/monitordata',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_monitordata_update(self):
        """Test case for monitordata_update

        
        """
        body = ''
        response = self.client.open(
            '/orchestrator/monitordata/{FederationID}'.format(FederationID=update_test_file_federation_id),
            method='PUT',
            data=json.dumps(body),
            content_type='application/octet-stream; charset=utf-8')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
