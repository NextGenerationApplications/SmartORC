from __future__ import absolute_import
from dynamic_orchestrator.test import BaseTestCase
import os

class TestAppModelController(BaseTestCase):
    """AppModelController integration test stubs"""

    test_file_app_id = 'AppModelFileID1'
    test_file_name = 'AppModel.yml'
    test_file_path = './'

    update_test_file_app_id = 'AppModelFileID1'
    update_test_file_name = 'AppModel2.yml'
    update_test_file_path = './'
    
    def test_appmodel_create(self):
        """Test case for appmodel_create

        
        """    
        data = dict(app_id = self.test_file_app_id, 
                    file = (open(os.path.join(self.test_file_path, self.test_file_name), 'rb'), self.test_file_name, 'text/plain'))
        
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
        data = dict(body=(open(os.path.join(self.update_test_file_path, self.update_test_file_name), 'rb'), self.update_test_file_name,'text/plain'))   
        response = self.client.open(
            '/orchestrator/appmodel/{app_id}'.format(app_id=self.update_test_file_app_id),
            method='PUT',
            data=data,
            content_type='text/plain')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
