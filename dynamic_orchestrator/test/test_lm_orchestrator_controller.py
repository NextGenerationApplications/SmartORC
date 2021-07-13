# coding: utf-8

from __future__ import absolute_import

from flask import json

#from dynamic_orchestrator.models.inline_response500 import InlineResponse500  # noqa: E501
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

    def test_orchestrator_lm_request_ovr(self):
        """Test case for orchestrator_lm_request_orbk       
        """      
        # set the parameters of the request_body to deploy the first two components for OramaVR use case 
        json_file = open('intermidietmodel-UC1.json')
        app_model = json.load(json_file)
        application_parameters = None
        body1 = RequestBody([{'component_name':'accordion-ovr-0-0-1-1234-signalingserver'}],'deploy',app_model,application_parameters)
           
        response1 = self.client.open(
            '/orchestrator/request',
            method='POST',
            data=json.dumps(body1),
            content_type='application/json')
        
        #put a request to kubernetes API to wait until the first service is up and running
        
        body2 = RequestBody([{'component_name':'accordion-ovr-0-0-1-1234-localservice'}],'deploy',app_model,application_parameters)
           
        response2 = self.client.open(
            '/orchestrator/request',
            method='POST',
            data=json.dumps(body2),
            content_type='application/json')
        
        body3 = RequestBody([{'component_name':'accordion-ovr-0-0-1-1234-relayserver'}],'deploy',app_model,application_parameters)
           
        response3 = self.client.open(
            '/orchestrator/request',
            method='POST',
            data=json.dumps(body3),
            content_type='application/json')

        self.assert200(response1,
                       'Response body is : ' + response1.data.decode('utf-8'))
        self.assert200(response2,
                       'Response body is : ' + response2.data.decode('utf-8'))
        self.assert200(response3,
                       'Response body is : ' + response3.data.decode('utf-8'))
        
    def test_orchestrator_lm_request_orbk(self):
        """Test case for orchestrator_lm_request_orbk    
        """      
        # set the parameters of the request_body to deploy a gameserver for Orbk use case 
        json_file = open('intermidietmodel-UC2.json')
        app_model = json.load(json_file)
        application_parameters = None
        body = RequestBody([{'component_name':'accordion-orbk-0-0-1-1234-gameserver'}],'deploy',app_model,application_parameters)
           
        response = self.client.open(
            '/orchestrator/request',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        
        
    def test_orchestrator_lm_request_plexus(self):
        """Test case for orchestrator_lm_request_plexus
        """      
        # set the parameters of the request_body to deploy the plexus application for Plexus use case 
        json_file = open('intermidietmodel-UC3.json')
        app_model = json.load(json_file)
        application_parameters = None
        body = RequestBody([{'component_name':'accordion-plexus-0-0-1-1234-localservice'}],'deploy',app_model,application_parameters)
           
        response = self.client.open(
            '/orchestrator/request',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

if __name__ == '__main__':
    import unittest
    unittest.main()
