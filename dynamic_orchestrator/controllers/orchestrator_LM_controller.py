import connexion
from dynamic_orchestrator.converter.Parser import ReadFile
from dynamic_orchestrator.converter.MatchingModel import generate
from dynamic_orchestrator.converter.Converter import namespace,secret_generation  
#from dynamic_orchestrator.models.inline_response500 import InlineResponse500  # noqa: E501
from dynamic_orchestrator.models.request_body import RequestBody
from dynamic_orchestrator.core.vim_sender_worker import vim_sender_worker
from flask import current_app
#from dynamic_orchestrator import util
#from  urllib.error import HTTPError
import base64
import json
import requests
from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator
from mip import OptimizationStatus
#from pickle import NONE
import ipaddress
#from symbol import except_clause
#from Configuration import Constants

def choose_application (name):   
    if name == 'accordion-plexus-0-0-1':
        return 'gitlab+deploy-token-420906', 'jwCSDnkoZDeZqwf2i9-m'
    if name == 'accordion-orbk-0-0-1':
        return 'gitlab+deploy-token-420904', 'gzP9s2bkJV-yeh1a6fn3'
    if name == 'accordion-ovr-0-0-3':
        return 'gitlab+deploy-token-430087', 'NDxnnzt9WvuR7zyAHchX'
    return None, None

def supported_operation (operation):
    if operation == 'deploy':
        return deploy
    if operation == 'terminate':
        return terminate
    return None
    

def secret (name):  
    token_name, token_pass = choose_application(name)
    if not token_name:
        return None 
    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    json_file = {
        "auths": {
            "https://registry.gitlab.com": {
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
            return MMM_response_json, None
        
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
     
            app_component_name = body.app_component_names[i].component_name
            app_component_name_parts = app_component_name.split('-')
              
            try:
                app_version = app_component_name_parts[2]+ '-' + app_component_name_parts[3] + '-'  + app_component_name_parts[4]
                app_name =   app_component_name_parts[0] + '-' + app_component_name_parts[1] + '-' + app_version
                if(i==0):
                    app_instance = app_name + '-' + app_component_name_parts[5]
                else:
                    if((app_name + '-' + app_component_name_parts[5]) != app_instance):
                        return None, None, 'Deploy operation not executed successfully: application components must be all of the same application'   
            except:
                return None, None, 'Deploy operation not executed successfully: application component name syntax does not follow ACCORDION conventions, or some parts are missing'     
        
        return app_name, app_instance, None
  
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
                        
        secret_string = secret(app_name)
               
        if not secret_string:
            error = 'Deploy operation not executed successfully: application ' + app_name + ' has not been uploaded on the ACCORDION platform '
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500      
        
        # Error handling to be finished
        current_app.config.get('LOGGER').info(" Request to Parser for App instance %s: parsing model function invoked " % app_instance)  
        try:
            nodelist, imagelist, app_version = ReadFile(body.app_model)
        except:
            error = 'Deploy operation not executed successfully: Application Model is not parsable'
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500 
        
        current_app.config.get('LOGGER').info(" Request to Parser for App instance %s: parsing model function terminated " % app_instance)  
        #for image in imagelist:
        #    print(str(image))
        current_app.config.get('LOGGER').info(" Request to Converter for App instance %s: matchmaking model function invoked" % app_instance)  
        
        matchmaking_model = generate(nodelist, app_instance)
        
        json_string = json.dumps(matchmaking_model)
        Kafka_Producer = Producer()
        Kafka_Producer.send_message('accordion.monitoring.reservedResources', json_string)
        
        
        current_app.config.get('LOGGER').info(" Request to Converter started for App instance %s: matchmaking model function terminated" % app_instance)  

        solver = ConcreteOrchestrator() 
        
        RID_response_json, error = send_RID_request()
        if(error):
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500    
        
        
        lat_qoe_levels = {}
        for parameter in body.application_parameters:
            if (parameter._device_ip):
                MMM_response_json, error = send_MMM_request(parameter._component_name, parameter._device_ip)
                if(error):
                    current_app.config.get('LOGGER').error(error + ". Returning code 500")
                    return {'reason': error}, 500
                lat_qoe_levels[parameter._component_name] = MMM_response_json
                
                    
        dep_plan, status = solver.calculate_dep_plan(current_app, body._app_component_names, RID_response_json, matchmaking_model, body._application_parameters, lat_qoe_levels)
        current_app.config.get('LOGGER').info(" Request to solver terminated to calculate deployment plan ")  
        
        if not dep_plan:
            error = 'Deploy operation not executed successfully: '
            error += dep_plan_status(status)
            current_app.config.get('LOGGER').error(error + ". Returning code 500")  
            return {'reason': error}, 500 

        current_app.config.get('LOGGER').debug(" Deployment plan: ")
                 
        namespace_yaml = namespace(app_instance)        
                
        secret_yaml = secret_generation(secret_string, app_instance)
                    
        vim_results = [[]] * len(dep_plan);
        
        vim_sender_workers_list = []
 
        current_app.config.get('LOGGER').info(" Initialization of threads started")  

        thread_id=0
        for EdgeMinicloud, component_list in dep_plan.items():
            current_app.config.get('LOGGER').debug(" Minicloud ID: %s" %EdgeMinicloud)
            current_app.config.get('LOGGER').debug(" Component name: %s " % component_list[0])
            vim_sender_workers_list.append(vim_sender_worker(current_app.config.get('LOGGER'), thread_id, app_instance, nodelist, imagelist,namespace_yaml, secret_yaml, EdgeMinicloud, component_list, vim_results))
            thread_id+=1
            
        current_app.config.get('LOGGER').info(" Initialization of threads finished correctly!")  
  
        thread_id=0
        for tid in vim_sender_workers_list:
            current_app.config.get('LOGGER').debug("Thread " + str(thread_id) + " launched!")  
            tid.start()
            thread_id+=1

        current_app.config.get('LOGGER').info(" Threads launched correctly!")  

        for tid in vim_sender_workers_list:
            tid.join()
            
        current_app.config.get('LOGGER').info(" Threads finished to calculate successfully!")  
           
        for vim_result in vim_results:
            for component_result in vim_result:
                for component_instance_name, date_or_error in component_result.items():
                    if isinstance(date_or_error,int):
                        # send component instance id and creation date time to ASR
                        current_app.config.get('LOGGER').info("Request to Application Status Registry started")      
                        request_to_ASR = {"id": component_instance_name, "creationTime": date_or_error, "externalIp": None, "resources": None }    
                        current_app.config.get('LOGGER').debug("Request sent to Application Status Registry for component instance " + component_instance_name  + " %s" % json.dumps(request_to_ASR)) 
                        current_app.config.get('LOGGER').debug("Request sent: PUT http://62.217.127.19:3000/v1/applicationComponentInstance")      
     
                        ASR_response = requests.put('http://62.217.127.19:3000/v1/applicationComponentInstance',timeout=5, data = json.dumps(request_to_ASR), headers={'Content-type': 'application/json'})
                        ASR_response.raise_for_status()
                        current_app.config.get('LOGGER').info("Request to Application Status Registry finished successfully!")   
                        current_app.config.get('LOGGER').debug("Request to Application Status Registry returned with response: %s" % ASR_response.text)                    
                    else:   
                        current_app.config.get('LOGGER').error('%s . Returning code 500' % date_or_error)                       
                        return {'reason': date_or_error}, 500               
             
    except requests.exceptions.Timeout as err:
        error = 'Deploy operation not executed successfully due to a timeout in the communication with the ASR!'
        current_app.config.get('LOGGER').error('Deploy operation not executed successfully due to a timeout in the communication with the ASR. Returning code 500')  
        return {'reason': error}, 500 
        
    except requests.exceptions.RequestException as err:
        error = 'Deploy operation not executed successfully due to the following internal server error in the communication with the ASR: ' + str(err)
        current_app.config.get('LOGGER').error(error + ". Returning code 500")
        return {'reason': error}, 500
    
    except OSError as err:
        if err:
            error = 'Deploy operation not executed successfully due to the following internal server error: ' + err.strerror
        else:
            error = 'Deploy operation not executed successfully due to an unknown internal server error! '
        current_app.config.get('LOGGER').error(error + ". Returning code 500")
        return {'reason': error}, 500
    
    except:
        error = 'Deploy operation not executed successfully due to an unknown internal server error!'
        current_app.config.get('LOGGER').error(error + ". Returning code 500")
        return {'reason': error}, 500
    
    current_app.config.get('LOGGER').info("------------------ Deploy request finished succesfully ---------------------")
    return 200

def terminate(body):
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
    current_app.config.get('LOGGER').debug('----------------------------------------------------------------')
    current_app.config.get('LOGGER').debug('Received a request for the Orchestrator from the LifeCycle Manager to be served')

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
    
