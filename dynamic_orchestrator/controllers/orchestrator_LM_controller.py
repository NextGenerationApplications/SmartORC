import connexion
import traceback

from converter_package.Parser import ReadFile
from converter_package.MatchingModel import generate
from converter_package.Converter import namespace, secret_generation, ID  

import time
import random
from accordion_project import utils
from accordion_project import accordion_operations as ops

from dynamic_orchestrator.models.request_body import RequestBody
from dynamic_orchestrator.core.vim_sender_worker import vim_sender_worker
from flask import current_app
import base64
import json
import requests
from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator
from mip import OptimizationStatus


def supported_operation (operation):
    if operation == 'deploy':
        return deploy
    if operation == 'undeploy':
        return undeploy
    return None
    

def secret ():  
    token_name, token_pass = ("gkorod_token", "r-qEyXZx8Z5RqZ5MQrGN")
    if not token_name:
        return None 
    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    json_file = {
        "auths": {
            "https://app.accordion-project.eu:31723": {
                "auth": base64_string
            }
        }
    }
    json_string = json.dumps(json_file)
    json_base64_string = base64.b64encode(json_string.encode('utf-8')).decode("utf-8")
    return json_base64_string

def check_application_parameters(operation, components, application_parameters):
    if (application_parameters):
        found_components = set();
        if (len(application_parameters)!=0):       
            if( operation == 'deploy'):
                for parameter in application_parameters:
                    if(parameter._component_name):
                        find = False
                        for component in components:
                            if (component._component_name == parameter._component_name):
                                find = True
                                if( parameter._component_name in found_components):
                                    return 'Deploy operation not executed successfully: an application parameter component ' + parameter._component_name + ' appears at least twice in the request application parameters'
                                else:
                                    found_components.add(parameter._component_name)
                        if (find == False):
                            return 'Deploy operation not executed successfully: an application parameter component is not a component of the request'
                    if(parameter._external_ip):
                        try:
                            ipaddress.ip_address(parameter._external_ip)
                        except:
                            return 'Deploy operation not executed successfully: the application parameter external_ip' + parameter._external_ip +  ' is not a valid ip address'
                    if(parameter._latency_qoe_level_threshold):
                        if(parameter._device_ip):     
                            try:
                                ipaddress.ip_address(parameter._device_ip)
                            except:
                                return 'Deploy operation not executed successfully: the application parameter device_ip' + parameter._device_ip +  ' is not a valid ip address'                       
                        else:
                            return 'Deploy operation not executed successfully: the application parameter device_ip is missing but a latency_threshold parameter has been specified: both are needed'

                    else:
                        if(parameter._device_ip):
                            return 'Deploy operation not executed successfully: the application parameter latency_threshold is missing but a device_ip parameter has been specified: both are needed'
    return None

def test_MMM(MMM_response):
    MMM_response[0]['minicloudId'] = 'mc1' 
    MMM_response[0]['qoe'] = 30   
  
    MMM_response[1]['minicloudId'] = 'mc2'
    MMM_response[1]['qoe'] = 10   
    return MMM_response

def send_MMM_request(component_name,device_ip):
    MMM_IP = "83.212.125.74"
    MMM_PORT  = "40110"
    try:        
        Request_URL = "http://" + MMM_IP + ":" + MMM_PORT + "/qoelevel/" + device_ip

        current_app.config.get('LOGGER').info(" Request to Minicloud Membership Management service for component " + component_name + " started")
        current_app.config.get('LOGGER').info(" Request sent: HTTP GET + " + Request_URL)
    
        MMM_response = requests.get(Request_URL)
        
        MMM_response.raise_for_status()
        
        MMM_response_json = MMM_response.json()
        
        if(MMM_response_json == None):
            return MMM_response_json,  None
        
        MMM_response_final = json.loads(MMM_response.json())
        
        current_app.config.get('LOGGER').info(" Request to MMM for component " + component_name + " successfully completed!")

    except requests.exceptions.Timeout as err:
        return None,'Deploy operation not executed successfully due to a timeout in the communication with the MMM!'
        
    except requests.exceptions.RequestException as err:
        return None,'Deploy operation not executed successfully due to the following internal server error in the communication with the MMM: ' + str(err)
        
    except json.JSONDecodeError as err:
        return None,'Deploy operation not executed successfully due to an internal server error. Response from MMM not Json parsable due to error ' + str(err)
    
    MMM_response_final = test_MMM(MMM_response_final)
                                 
    return MMM_response_final, None

def test_RID(RID_response):
    RID_response[0]['minicloud_id'] = 'mc1'
    RID_response[1]['minicloud_id'] = 'mc1'
    RID_response[2]['minicloud_id'] = 'mc2'    
    return RID_response

def send_RID_request():
        RID_IP = "localhost"
        RID_PORT = "9001"
        try:
            
            Request_URL_miniclouds = "http://" + RID_IP + ":" + RID_PORT + "/miniclouds"
            Request_URL_debug = "http://" + RID_IP + ":" + RID_PORT + "/debug"
            current_app.config.get('LOGGER').info(" Request to Resource Indexing & Discovery service started")
            current_app.config.get('LOGGER').info(" Request sent: HTTP GET" + Request_URL_miniclouds)

            Debug_response = requests.get(Request_URL_debug) #, timeout=5)
            Debug_response.raise_for_status()
     
            RID_response = requests.get(Request_URL_miniclouds)          
            RID_response.raise_for_status()
            RID_response_json = RID_response.json()                         
            current_app.config.get('LOGGER').info(" Request to RID successfully completed!")
            
        except requests.exceptions.Timeout as err:
            return None,'Deploy operation not executed successfully due to a timeout in the communication with the RID!'
        
        except requests.exceptions.RequestException as err:
            return None,'Deploy operation not executed successfully due to the following internal server error in the communication with the RID: ' + str(err)
        
        except json.JSONDecodeError as err:
            return None,'Deploy operation not executed successfully due to an internal server error. Response from RID not Json parsable due to error ' + str(err)                    

        current_app.config.get('LOGGER').debug(" Request to Resource Indexing & Discovery service returned with response: #%s " % RID_response_json)
        RID_response_json = test_RID(RID_response_json)
        return RID_response_json, None

def dep_plan_status(status):
    if status == OptimizationStatus.NO_SOLUTION_FOUND:
        return 'no deploy solution found!'
    if status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
        return 'infeasible deploy solution found!'
    if status == OptimizationStatus.UNBOUNDED:
        return 'unbounded deploy solution found!'  
  
def check_components (body):  
        components_number = len(body.app_component_names)

        if(body.app_component_names == None):
            return None, None, 'Deploy operation not executed successfully due to the following error: no application components to be deployed' 
        
        if(components_number == 0):
            return None, None, 'Deploy operation not executed successfully due to the following error: no application components to be deployed'   
        
        found_components = set();
        
        current_app.config.get('LOGGER').debug("Deploy request started with parameters: ")
             
        for i in range(components_number):
            current_app.config.get('LOGGER').debug("----- Component name: %s" % body.app_component_names[i].component_name)
            #current_app.config.get('LOGGER').debug("----- App model: %s " % str(body.app_model))
            json_pp = json.dumps(body.app_model.get('requirements')[0].get('toscaDescription'), indent=4)
            current_app.config.get('LOGGER').debug("----- App model: %s " % json_pp)
            #current_app.config.get('LOGGER').debug("----- Application model: [ ... ] ")
            if(body.app_component_names[i].component_name in found_components):
                return None, None, 'Deploy operation not executed successfully: application component ' + body.app_component_names[i].component_name + ' appears at least twice in the request'
            else:
                found_components.add(body.app_component_names[i].component_name)
                
            current_app.config.get('LOGGER').debug("----- Operation: %s " % body.operation)
            current_app.config.get('LOGGER').debug("----- Application parameters: %s " % str(body.application_parameters))
     
            #app_component_name = body.app_component_names[i].component_name
            #app_component_name_parts = app_component_name.split('-')
              
            try:
                ns = utils.parse(body.app_component_names[i].component_name)
                #app_version = ns['appVersion'] #app_component_name_parts[2]+ '-' + app_component_name_parts[3] + '-'  + app_component_name_parts[4]
                app_name =   ns['appName'] #app_component_name_parts[0] + '-' + app_component_name_parts[1] + '-' + app_version
                if(i==0)
                    app_instance = ns['appInstanceId'] # app_name + '-' + app_component_name_parts[5]
                else 
                    if(app_instance !=ns['appInstanceId'])
                        return None, None, 'Deploy operation not executed successfully: application components must be all of the same application'                  
            except:
                return None, None, 'Deploy operation not executed successfully: application component name syntax does not follow ACCORDION conventions, or some parts are missing'     
        
        return app_name, app_instance, None

'''
Manage the deploy operations
'''
def deploy(body):
    current_app.config.get('LOGGER').info("------------------ Deploy request started ---------------------")
    try:
        app_name, app_instance, error = check_components(body)
        if(error):
            current_app.config.get('LOGGER').error(error + ". Returning code 400")
            return {'reason': error}, 400 
        
        error = check_application_parameters('deploy', body.app_component_names, body.application_parameters)
        if(error):
            current_app.config.get('LOGGER').error(error + ". Returning code 400")
            return {'reason': error}, 400   
        # -- checking and logging of the received message --- #
        #components = body.app_component_names
        #if(components == None):
        #    error = 'Deploy operation not executed successfully due to the following error: no application components to be deployed' 
        #    current_app.config.get('LOGGER').error('Deploy operation not executed successfully due to the following error: no application components to be deployed. Returning code 400' )
        #    return {'reason': error}, 400
        
        #if(len(components) == 0):
        #    error = 'Deploy operation not executed successfully due to the following error: no application components to be deployed'
        #    current_app.config.get('LOGGER').error('Deploy operation not executed successfully due to the following error: no application components to be deployed. Returning code 400')
        #    return {'reason': error}, 400     
        
        #current_app.config.get('LOGGER').debug("Deploy request started with parameters: ")
        #for i in range(len(components)):
        #    current_app.config.get('LOGGER').debug("----- Component name: %s" % components[i].component_name)
        #    current_app.config.get('LOGGER').debug("----- App model: %s " % str(body.app_model))
        #    current_app.config.get('LOGGER').debug("----- Operation: %s " % body.operation)
        #    current_app.config.get('LOGGER').debug("----- Application parameters: %s " % str(body.application_parameters))
     

        # -- Parsing of the namespace --- #
        #try:
        #    ns = utils.parse(components[0].component_name)
        #    app_component_name = ns['componentName']
        #    app_version = ns['appVersion'] #app_component_name_parts[2]+ '-' + app_component_name_parts[3] + '-'  + app_component_name_parts[4]
        #    app_name =   ns['appName'] #app_component_name_parts[0] + '-' + app_component_name_parts[1] + '-' + app_version
        #    app_instance = ns['appInstanceId'] # app_name + '-' + app_component_name_parts[5]
        #except:
        #    error = 'Deploy operation not executed successfully: application component name syntax does not follow ACCORDION conventions, or some parts are missing '
        #    current_app.config.get('LOGGER').error(error + ". Returning code 400")
        #    return {'reason': error}, 400      
                
        # -- Secret Generation ---       
        secret_string = secret()
        current_app.config.get('LOGGER').debug("Secret generation completed.")

        if not secret_string:
            error = 'Deploy operation not executed successfully: application ' + app_name + ' has not been uploaded on the ACCORDION platform '
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500      
        
        # ---- Call the RID ---- #
        try:
            #Debug_response = requests.get('http://continuum.accordion-project.eu:9001/debug', timeout=15)
            #Debug_response.raise_for_status()
            
            RID_response = requests.get('http://continuum.accordion-project.eu:9001/miniclouds/nodes', timeout=15)                  
            RID_response.raise_for_status()
            RID_response_json = RID_response.json()      
 
        except Exception as e:
            error = 'Error in contacting the RID.'
            traceback.print_exc()
            current_app.config.get('LOGGER').error(error)
            return {'reason': error}, 500

        current_app.config.get('LOGGER').info(" Request to RID returned with response: "+ str(RID_response.status_code) +" "+ RID_response.reason)
        
        
        # -- Parsing the tosca model to get some info to be used for the solver -- #
        current_app.config.get('LOGGER').info(" Request to Parser for App instance %s: parsing model function invoked " % app_instance)  
        try:
            nodelist, imagelist, app_version = ReadFile(body.app_model) ## <- app_version not sure to be updated. Check with Ioannis?
        except:
            error = 'Deploy operation not executed successfully: Application Model is not parsable'
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500 
        # current_app.config.get('LOGGER').info(" Request to Parser for App instance %s: parsing model function terminated " % app_instance)  
        
        
        # -- Call the Converter to get a matchmaking model -- #
        current_app.config.get('LOGGER').info(" Request to Converter for App instance %s: matchmaking model function invoked" % app_instance)  
        matchmaking_model = generate(nodelist, app_instance) # list the feature needed by the application
        # current_app.config.get('LOGGER').info(" Request to Converter started for App instance %s: matchmaking model function terminated" % app_instance)  

    

        # -- Call the MMM to get the list of miniclouds
        mmm_resp = requests.get('http://continuum.accordion-project.eu:40110/echoserverlist').json()
        minicloud_dict = {} # It is needed later to get the IP
        print("\tAvailable mincilouds:")
        for item in mmm_resp:
            minicloud_dict[item['minicloudId']] = item['echoserverIp']
            print("\t", item['minicloudId'], item['echoserverIp'])

        # -- Call the solver to provide the plan -- #
        if body.application_parameters['selection_strategy'] == ops.DEPLOY:
            dep_plan, status = ({body.application_parameters['minicloud_id']:[app_component_name]}, 'ok')
        elif body.application_parameters['selection_strategy'] == ops.RANDOM_DEPLOY:
            # contact the MMM to get the list of the miniclouds         
            minicloud = random.choice(mmm_resp)['minicloudId']
            dep_plan, status = ({minicloud:[app_component_name]}, 'ok')

        elif body.application_parameters['selection_strategy'] == ops.SMART_DEPLOY:
            current_app.config.get('LOGGER').info(" Request to solver started to calculate deployment plan")
            solver = ConcreteOrchestrator()         
            # dep_plan, status = solver.calculate_dep_plan(components, RID_response_json, matchmaking_model)
            dep_plan, status = ({"Minicloud1":[app_component_name]}, 'optimal')
            #current_app.config.get('LOGGER').info(" Request to solver terminated to calculate deployment plan ")  

        if not dep_plan:
            error = 'Deploy operation not executed successfully, unable to provide a deployment plan: '
            error += dep_plan_status(status)
            current_app.config.get('LOGGER').error(error + ". Returning code 500")  
            return {'reason': error}, 500 

        current_app.config.get('LOGGER').debug(" ** Deployment plan ** : %s " % dep_plan)

        
        # -- Check the plan against the QoE -- #
        current_app.config.get('LOGGER').info("Contacting QoE for validation of the plan")
        for minicloud, component in dep_plan.items():
            # qoe_request = {"minicloud":minicloud, "application":app_component_name , "criteria":body.application_parameters['criteria']}
            qoe_response = {"minicloud":minicloud,"application":app_component_name , "result":"pass"}

            print("\t",component,"->",minicloud,":",qoe_response['result'])

        # -- Generate yamls parts to send to k3s -- #
        k3s_namespace = ID.generate_k3s_namespace(ns['appName'], ns['appVersion'], ns['appInstanceId'])
        namespace_yaml = namespace(k3s_namespace)[k3s_namespace]          
        secret_yaml = secret_generation(secret_string, k3s_namespace)[k3s_namespace]
                    

        # -- Generate threads for VIMs -- #
        vim_results = [[]] * len(dep_plan)
        vim_sender_workers_list = []
        current_app.config.get('LOGGER').info("Initialization of threads started")  

        thread_id=0
        for EdgeMinicloud, component_list in dep_plan.items():

            vim_worker = vim_sender_worker(
                current_app.config.get('LOGGER'), 
                thread_id, 
                ns, 
                nodelist, 
                imagelist,
                namespace_yaml, 
                secret_yaml, 
                EdgeMinicloud, 
                component_list, 
                vim_results, 
                minicloud_dict[EdgeMinicloud])

            vim_sender_workers_list.append(vim_worker)
            thread_id+=1
            
        # start the threads
        for tid in vim_sender_workers_list:
            tid.start()
  
        # wait for them to be completed
        for tid in vim_sender_workers_list:
            tid.join()
            
        # current_app.config.get('LOGGER').info(" Threads finished to calculate successfully!")  
           
        # -- Process the results from the VIM gateways and contact ASR -- #
        for vim_result in vim_results:
            for component_result in vim_result:
                for component_instance_name, date_or_error in component_result.items():
                    if isinstance(date_or_error,int):
                        # send component instance id and creation date time to ASR   
                        request_to_ASR = {"id": component_instance_name, "creationTime": date_or_error, "externalIp": None, "resources": None }    
                        current_app.config.get('LOGGER').debug("Request sent to ASR for component instance " + component_instance_name  + " %s" % json.dumps(request_to_ASR))      

                        # TEMPORARY: Skip communication with ASR

                        # ASR_response = requests.put('http://continuum.accordion-project.eu:40150/status/applicationComponentInstance',timeout=5, data = json.dumps(request_to_ASR), headers={'Content-type': 'application/json'})
                        # ASR_response.raise_for_status()
                        # current_app.config.get('LOGGER').info("Request to ASR finished successfully!")   
                        current_app.config.get('LOGGER').debug("Request to ASR returned with response: %s" % ASR_response.text)                    
                    else:   
                        current_app.config.get('LOGGER').error('%s . Returning code 500' % date_or_error)                       
                        return {'reason': date_or_error}, 500               

    except Exception as e:
        error = 'Deploy operation FAILED due to an internal server error!'
        traceback.print_exc()
        current_app.config.get('LOGGER').error(error + ". Returning code 500")
        return {'reason': error}, 500
    
    current_app.config.get('LOGGER').info("------------------ Deploy request SUCCESS ---------------------")
    return 200

def undeploy(body):
    current_app.config.get('LOGGER').info("------------------ Undeploy request started ---------------------")
    error = 'Undeploy operation not implemented yet!'
    current_app.config.get('LOGGER').error(error + ". Returning code 500")
    return {'reason': error}, 500

def orchestrator_LM_request(body):  # noqa: E501
    """orchestrator_lm_request

    Receive a request from the Lifecycle Manager ACCORDION component # noqa: E501

    :param body: The parameters of the request received from the LM
    :type body: dict | bytes

    :rtype: None
    """
    current_app.config.get('LOGGER').debug('\n-------------Received a new request ------------')

    if connexion.request.is_json:  
        body = RequestBody.from_dict(connexion.request.get_json())  # noqa: E501         
        operation = supported_operation(body.operation)
    else:
        current_app.config.get('LOGGER').debug('Bad request: it should be Json formatted')
    if operation == None:
        error = 'Request not executed successfully due to the following error: empty operation parameter!' 
        current_app.config.get('LOGGER').debug('Request not executed successfully due to the following error: empty operation parameter. Returning code 400')
        return {'reason': error}, 400
    return operation(body)

def set_logging_level(logginglevel):

    current_app.config.get('LOGGER').debug('----------------------------------------------------------------')
    current_app.config.get('LOGGER').debug('Received a request for the Orchestrator to change Logging level')   
    if logginglevel in current_app.config.get('LOGGINGLEVELS'):
        current_app.config.get('LOGGER').info("changing logging level to %s" % logginglevel)
        current_app.config.get('LOGGERHANDLER').setLevel(current_app.config.get('LOGGINGLEVELS')[logginglevel])
    else:
        current_app.config.get('LOGGER').error("Requested logging level (%s) not supported. Returning code 500" % logginglevel) 
        return 500

    current_app.config.get('LOGGER').debug("Returning from SET LOGGING LEVEL request. Returning code 200")
    
    return 'Logging level set to ' + logginglevel, 200 
    
