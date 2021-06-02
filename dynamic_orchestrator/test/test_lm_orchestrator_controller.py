# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from dynamic_orchestrator.models.inline_response500 import InlineResponse500  # noqa: E501
from dynamic_orchestrator.models.request_body import RequestBody  # noqa: E501
from dynamic_orchestrator.test import BaseTestCase


    

class TestLMOrchestratorController(BaseTestCase):
    """LMOrchestratorController integration test stubs"""
    
    def pretty_print(self,req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        print('{}\n{}\r\n{}\r\n\r\n{}'.format(
            '-----------START-----------',
            req.request.method + ' ' + req.request.url,
            '\r\n'.join('{}: {}'.format(k, v) for k, v in req.request.headers.items()),
            req.request.body,
        ))
    
    def test_orchestrator_lm_request(self):
        """Test case for orchestrator_lm_request

        
        """
        body = RequestBody()
        response = self.client.open(
            '/request',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
