import connexion
import traceback

from converter_package.Parser import ReadFile
from converter_package.MatchingModel import generate
from converter_package.Converter import namespace,secret_generation  


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

def choose_application (name):   
    if name == 'accordion-plexus-0-0-1':
        return 'gitlab+deploy-token-420906', 'jwCSDnkoZDeZqwf2i9-m'
    if name == 'accordion-orbk-0-0-1':
        return 'gitlab+deploy-token-420904', 'gzP9s2bkJV-yeh1a6fn3'
    if name == 'accordion-ovr-0-0-3':
        return 'gitlab+deploy-token-430087', 'NDxnnzt9WvuR7zyAHchX'
    if name == 'accordion-Barcelona_UC1_RI-0-0-3':
        return 'gitlab+deploy-token-430087', 'NDxnnzt9WvuR7zyAHchX'
    return None, None

def supported_operation (operation):
    if operation == 'deploy':
        return deploy
    if operation == 'undeploy':
        return undeploy
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

def dep_plan_status(status):
    if status == OptimizationStatus.NO_SOLUTION_FOUND:
        return 'no deploy solution found!'
    if status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
        return 'infeasible deploy solution found!'
    if status == OptimizationStatus.UNBOUNDED:
        return 'unbounded deploy solution found!'  
  
def deploy(body):
    current_app.config.get('LOGGER').info("------------------ Deploy request started ---------------------")
    try:
        components = body.app_component_names
        if(components == None):
            error = 'Deploy operation not executed successfully due to the following error: no application components to be deployed' 
            current_app.config.get('LOGGER').error('Deploy operation not executed successfully due to the following error: no application components to be deployed. Returning code 400' )
            return {'reason': error}, 400
        
        if(len(components) == 0):
            error = 'Deploy operation not executed successfully due to the following error: no application components to be deployed'
            current_app.config.get('LOGGER').error('Deploy operation not executed successfully due to the following error: no application components to be deployed. Returning code 400')
            return {'reason': error}, 400     
        
        current_app.config.get('LOGGER').debug("Deploy request started with parameters: ")
        for i in range(len(components)):
            current_app.config.get('LOGGER').debug("----- Component name: %s" % components[i].component_name)
            current_app.config.get('LOGGER').debug("----- App model: %s " % str(body.app_model))
            current_app.config.get('LOGGER').debug("----- Operation: %s " % body.operation)
            current_app.config.get('LOGGER').debug("----- Application parameters: %s " % str(body.application_parameters))
     
        app_component_name = components[0].component_name
        app_component_name_parts = app_component_name.split('-')
        
        try:
            app_version = app_component_name_parts[2]+ '-' + app_component_name_parts[3] + '-'  + app_component_name_parts[4]
            app_name =   app_component_name_parts[0] + '-' + app_component_name_parts[1] + '-' + app_version
            app_instance = app_name + '-' + app_component_name_parts[5]
        except:
            error = 'Deploy operation not executed successfully: application component name syntax does not follow ACCORDION conventions, or some parts are missing '
            current_app.config.get('LOGGER').error(error + ". Returning code 400")
            return {'reason': error}, 400      
                
                
                        
        secret_string = secret(app_name)
               
        if not secret_string:
            error = 'Deploy operation not executed successfully: application ' + app_name + ' has not been uploaded on the ACCORDION platform '
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500      
                    
        try:
            current_app.config.get('LOGGER').info(" Request to RID started")

            Debug_response = requests.get('http://continuum.accordion-project.eu:9001/debug', timeout=5)
            Debug_response.raise_for_status()
            
            RID_response = requests.get('http://continuum.accordion-project.eu:9001/miniclouds') #, timeout=5)                  
            RID_response.raise_for_status()
            RID_response_json = RID_response.json()                         
            current_app.config.get('LOGGER').info(" Request to RID finished successfully!")
            
        except requests.exceptions.Timeout as err:
            error = 'Deploy operation not executed successfully due to a timeout in the communication with the RID!'
            current_app.config.get('LOGGER').error('Deploy operation not executed successfully due to a timeout in the communication with the RID. Returning code 500')  
            return {'reason': error}, 500 
        
        except requests.exceptions.RequestException as err:
            error = 'Deploy operation not executed successfully due to the following internal server error in the communication with the RID: ' + str(err)
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500
        
        except json.JSONDecodeError as err:
            error = 'Deploy operation not executed successfully due to an internal server error. Response from RID not Json parsable due to error ' + str(err)
            current_app.config.get('LOGGER').error(error + ". Returning code 500")
            return {'reason': error}, 500
        
        current_app.config.get('LOGGER').debug(" Request to RID returned with response: %s " % RID_response_json)
        
        
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
        current_app.config.get('LOGGER').info(" Request to Converter started for App instance %s: matchmaking model function terminated" % app_instance)  

        solver = ConcreteOrchestrator() 
        
        current_app.config.get('LOGGER').info(" Request to solver started to calculate deployment plan ")  
        dep_plan, status = solver.calculate_dep_plan(components, RID_response_json, matchmaking_model)
        current_app.config.get('LOGGER').info(" Request to solver terminated to calculate deployment plan ")  
        
        if not dep_plan:
            error = 'Deploy operation not executed successfully: '
            error += dep_plan_status(status)
            current_app.config.get('LOGGER').error(error + ". Returning code 500")  
            return {'reason': error}, 500 

        current_app.config.get('LOGGER').debug(" Deployment plan: %s " % dep_plan)   
                 
        namespace_yaml = namespace(app_instance)        
                
        secret_yaml = secret_generation(secret_string, app_instance)
                    
        vim_results = [[]] * len(dep_plan);
        
        vim_sender_workers_list = []
 
        current_app.config.get('LOGGER').info(" Initialization of threads started")  

        thread_id=0
        for EdgeMinicloud, component_list in dep_plan.items():
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
                        current_app.config.get('LOGGER').info("Request to ASR started")      
                        request_to_ASR = {"id": component_instance_name, "creationTime": date_or_error, "externalIp": None, "resources": None }    
                        current_app.config.get('LOGGER').debug("Request sent to ASR for component instance " + component_instance_name  + " %s" % json.dumps(request_to_ASR))      
                        ASR_response = requests.put('http://62.217.127.19:3000/v1/applicationComponentInstance',timeout=5, data = json.dumps(request_to_ASR), headers={'Content-type': 'application/json'})
                        ASR_response.raise_for_status()
                        current_app.config.get('LOGGER').info("Request to ASR finished successfully!")   
                        current_app.config.get('LOGGER').debug("Request to ASR returned with response: %s" % ASR_response.text)                    
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
            error = 'A Deploy operation not executed successfully due to the following internal server error: ' + err.strerror
        else:
            error = 'B Deploy operation not executed successfully due to an unknown internal server error! '
        current_app.config.get('LOGGER').error(error + ". Returning code 500")
        return {'reason': error}, 500
    
    except Exception as e:
        error = 'C Deploy operation not executed successfully due to an unknown internal server error!'
        traceback.print_exc()
        current_app.config.get('LOGGER').error(error + ". Returning code 500")
        return {'reason': error}, 500
    
    current_app.config.get('LOGGER').info("------------------ Deploy request finished succesfully ---------------------")
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
    current_app.config.get('LOGGER').debug('----------------------------------------------------------------')
    current_app.config.get('LOGGER').debug('Received a request for the Orchestrator to be served')

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
    
