import connexion
from dynamic_orchestrator.converter.Parser import ReadFile
from dynamic_orchestrator.converter.MatchingModel import generate
from dynamic_orchestrator.models.request_body import RequestBody
from flask import current_app
import requests
from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator
from mip import OptimizationStatus
from timeit import default_timer as timer
from random import randint

start_time = 0
end_time = 0
start_time_regrouped = 0
end_time_regrouped = 0

def supported_operation (operation):
    if operation == 'deploy':
        return deploy
    if operation == 'terminate':
        return terminate
    return None

def dep_plan_status(status):
    if status == OptimizationStatus.NO_SOLUTION_FOUND:
        return 'no deploy solution found!'
    if status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE:
        return 'infeasible deploy solution found!'
    if status == OptimizationStatus.UNBOUNDED:
        return 'unbounded deploy solution found!'  
  
def prepare_tests (app_instance, num_nodes, num_comps, regrouping_factor):
    
    #architectures = ['x86_64','ARM']
    architectures = ['x86_64']
    #oses = ['linux','windows']
    oses = ['linux']
    
    app_model = {"details":{"id":"1","name":"p","version":"0.0.3","isLatest":"true" },                
        "registry":[{"repository":"r","version":"latest","id":"2","size":"1MB","imageName":"s","component":"C1"}],
        "requirements":[{ "environment":"",
                                  "toscaDescription": { "tosca_definitions_version": "tosca_simple_yaml_1_2","description": "","imports": ["definitions/custom_types.yaml"],
  "topology_template": 
    {
        "inputs": {"ip": {"type": "string","description": "IP","required": False } },
        "node_templates": 
        {
            "Cloud_Framework": 
            {
                "type": "ACCORDION.Cloud_Framework",
                "properties": 
                {
                    "application":"p",
                    "deployment_phase": 
                    [           
                        {
                            "name":"pr",
                            "components": []
                        }
                    ]
                }
            }
        }
    }
 }
}],
        "metadata":{ "createdAt":"", "createdBy":"", "modifiedAt":"", "modifiedBy":"" }}
    
    component_names = []  
    component_reqs = []    
    for num in range(num_comps):  
        component_names.append(app_instance + "-c" +str(num))
        app_model["requirements"][0]["toscaDescription"]["topology_template"]["node_templates"]["Cloud_Framework"]["properties"]["deployment_phase"][0]["components"].append({"component": "C" + str(num),"type": "VM"})
        app_model["requirements"][0]["toscaDescription"]["topology_template"]["node_templates"]["C" + str(num)] =  {"type": "Component","properties":{
          "name": "c" +str(num),
          "application": "p",
          "external_ip": True,
          "daemon_set": False,
          "ip": {"get_input": "ip"},
          "deployment_unit": "VM",
          "flavor": "win2k12-iso",
          "port": [1]
        },"requirements":[{"host": "EdgeNode" + str(num)}]}
        
        num_cpus = randint(1,8)
        mem_size = randint(128, 1024)
        disk_size = randint(10,128)
        architecture = randint(0,len(architectures)-1)
        os = randint(0,len(oses)-1)
        
        component_reqs.append([num_cpus,mem_size,disk_size,architecture,os])
        
        app_model["requirements"][0]["toscaDescription"]["topology_template"]["node_templates"]["EdgeNode" + str(num)] =  {
        "type": "tosca.nodes.Compute.EdgeNode",
        "capabilities": 
        {
          "host": 
          {
            "properties": 
            {
              "num_cpus": num_cpus,
              "mem_size": str(mem_size) + "MB",
              "disk_size": str(disk_size) + "GB"
            }
          },
          "os": 
          {
            "properties": 
            {
              "architecture": architectures[architecture],
              "type": oses[os]
            }
          }
        }
      }
     
     
    if regrouping_factor > 0:
        component_names_regrouped = []
        app_model_regrouped = {"details":{"id":"1","name":"p","version":"0.0.3","isLatest":"true" },                
        "registry":[{"repository":"r","version":"latest","id":"2","size":"1MB","imageName":"s","component":"C1"}],
        "requirements":[{ "environment":"",
                                  "toscaDescription": { "tosca_definitions_version": "tosca_simple_yaml_1_2","description": "","imports": ["definitions/custom_types.yaml"],
  "topology_template": 
    {
        "inputs": {"ip": {"type": "string","description": "IP","required": False } },
        "node_templates": 
        {
            "Cloud_Framework": 
            {
                "type": "ACCORDION.Cloud_Framework",
                "properties": 
                {
                    "application":"p",
                    "deployment_phase": 
                    [           
                        {
                            "name":"pr",
                            "components": []
                        }
                    ]
                }
            }
        }
    }
 }
}],
        "metadata":{ "createdAt":"", "createdBy":"", "modifiedAt":"", "modifiedBy":"" }}
        
        for num in range((num_comps//regrouping_factor)):
            component_reqs_regrouped = [0,0,0,'x86_64','linux']
            component_names_regrouped.append(app_instance + "-c" +str(num))
            for i in range(regrouping_factor):
                j = (regrouping_factor * num) + i
                component_reqs_regrouped[0] += component_reqs[j][0]
                component_reqs_regrouped[1] += component_reqs[j][1]
                component_reqs_regrouped[2] += component_reqs[j][2]
                
            app_model_regrouped["requirements"][0]["toscaDescription"]["topology_template"]["node_templates"]["Cloud_Framework"]["properties"]["deployment_phase"][0]["components"].append({"component": "C" + str(num),"type": "VM"})
            app_model_regrouped["requirements"][0]["toscaDescription"]["topology_template"]["node_templates"]["C" + str(num)] =  {"type": "Component","properties":{
                "name": "c" +str(num),
                "application": "p",
                "external_ip": True,
                "daemon_set": False,
                "ip": {"get_input": "ip"},
                "deployment_unit": "VM",
                "flavor": "win2k12-iso",
                "port": [1]
                },"requirements":[{"host": "EdgeNode" + str(num)}]}
            
            app_model_regrouped["requirements"][0]["toscaDescription"]["topology_template"]["node_templates"]["EdgeNode" + str(num)] =  {
        "type": "tosca.nodes.Compute.EdgeNode",
        "capabilities": 
        {
          "host": 
          {
            "properties": 
            {
              "num_cpus": component_reqs_regrouped[0],
              "mem_size": str(component_reqs_regrouped[1]) + "MB",
              "disk_size": str(component_reqs_regrouped[2]) + "GB"
            }
          },
          "os": 
          {
            "properties": 
            {
              "architecture": component_reqs_regrouped[3],
              "type": component_reqs_regrouped[4]
            }
          }
        }
      }       
        
    #node_architectures = ['x86_64','ARM']
    node_architectures = ['x86_64']
    
    #node_oses = ['Linux','windows']
    node_oses = ['Linux']
        
    node_architecture = randint(0,len(node_architectures)-1)
        
    node_os= randint(0,len(node_oses)-1)
         
    cores = randint(20,100)
    
    ram  =  randint(2048000000000,4096000000000)
     
    disk =  randint(200000000000, 1000000000000)
     
    cpu_usage = 0.00
    
    nodes_description = [ 
    {'node_name': 'giannis0', 
      'node_cpu_arch': node_architectures[node_architecture], 
      'node_cpu_cores': cores, 
      'node_ram_total_bytes': ram,
      'node_disk_total_size': disk,
      'node_os_name':  node_oses[node_os], 
      'cpu_usage(percentage)': cpu_usage, 
      'available_memory(bytes)': ram, 
      'disk_free_space(bytes)': disk, 
      'minicloud_id': 'mc1'}
    ]
        
    for num in range(num_nodes):
        nodes_description.append({'node_name': 'giannis'+str(num), 
        'node_cpu_arch': node_architectures[node_architecture], 
        'node_cpu_cores': cores, 
        'node_ram_total_bytes': ram, 
        'node_disk_total_size': disk, 
        'node_os_name': node_oses[node_os], 
        'cpu_usage(percentage)': cpu_usage, 
        'available_memory(bytes)': ram,  
        'disk_free_space(bytes)':  disk, 
        'minicloud_id': 'mc1'})
    
    if regrouping_factor > 0:
        nodes_description_regrouped = [ 
    {'node_name': 'giannis0', 
      'node_cpu_arch': node_architectures[node_architecture], 
      'node_cpu_cores': cores*regrouping_factor, 
      'node_ram_total_bytes': ram*regrouping_factor,
      'node_disk_total_size': disk*regrouping_factor,
      'node_os_name':  node_oses[node_os], 
      'cpu_usage(percentage)': cpu_usage*regrouping_factor, 
      'available_memory(bytes)': ram*regrouping_factor, 
      'disk_free_space(bytes)': disk*regrouping_factor, 
      'minicloud_id': 'mc1'}
    ]
        for num in range((num_nodes//regrouping_factor)-1):
            nodes_description_regrouped.append({'node_name': 'giannis'+str(num), 
        'node_cpu_arch': node_architectures[node_architecture], 
        'node_cpu_cores': cores*regrouping_factor, 
        'node_ram_total_bytes': ram*regrouping_factor, 
        'node_disk_total_size': disk*regrouping_factor, 
        'node_os_name': node_oses[node_os], 
        'cpu_usage(percentage)': cpu_usage*regrouping_factor, 
        'available_memory(bytes)': ram*regrouping_factor,  
        'disk_free_space(bytes)':  disk*regrouping_factor, 
        'minicloud_id': 'mc1'})
            
        
    return component_names,nodes_description, app_model, component_names_regrouped, nodes_description_regrouped, app_model_regrouped,  
  
#TODO: remove external IP from the request and from the openapi3.0 interface file  
  
def deploy(body):
    app_instance = 'accordion-p-0-0-3-165'
    filename = "results.csv"
    # tests  = [{NUM_REPETITIONS, NUM_NODES, NUM_COMPS}, ... ]
    tests = [[5,30,10,5],[5,20,5,0]]
    
    f = open(filename, "w")
    
    for test in tests:
        for i in range(test[0]):
            
            component_names, resources, app_model, component_names_regrouped, resources_regrouped, app_model_regrouped = prepare_tests (app_instance, test[1], test[2], test[3]) 
             
            current_app.config.get('LOGGER').info("------------------ Deploy request started ---------------------")
            try:
                        
                try:
                    nodelist, imagelist, app_version = ReadFile(app_model)
                    if(test[3]>0):
                        nodelist_regrouped, imagelist_regrouped, app_version_regrouped = ReadFile(app_model_regrouped)

                except:
                    error = 'Deploy operation not executed successfully: Application Model is not parsable'
                    current_app.config.get('LOGGER').error(error + ". Returning code 500")
                    return {'reason': error}, 500 
                
                matchmaking_model = generate(nodelist, app_instance)
                if(test[3]>0):
                    matchmaking_model_regrouped = generate(nodelist_regrouped, app_instance)
 
                                            
                start_time = timer()
                solver = ConcreteOrchestrator()                 
                dep_plan, status = solver.calculate_dep_plan(current_app, component_names, resources, matchmaking_model)
                end_time = timer()                
                line = str(test[1]) + "," + str(test[2]) +"," + str(test[3]) + "," +str(end_time - start_time)+ "," + str(end_time_regrouped - start_time_regrouped) +","+str(status.name)+",NOREGROUPED\n"
                print(status)
                print(end_time - start_time)
                
                if(test[3]>0):
                    start_time_regrouped = timer()
                    solver = ConcreteOrchestrator()                 
                    dep_plan_regrouped, status_regrouped = solver.calculate_dep_plan(current_app, component_names_regrouped, resources_regrouped, matchmaking_model_regrouped)           
                    end_time_regrouped = timer()
                    line = str(test[1]) + "," + str(test[2]) +"," + str(test[3]) + "," +str(end_time - start_time)+ "," + str(end_time_regrouped - start_time_regrouped) +","+status.name+","+status_regrouped.name+"\n"
                    
                f.write(line)                                                                 
                current_app.config.get('LOGGER').info(" Request to solver terminated to calculate deployment plan ")                 
                     
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
    f.close()
    current_app.config.get('LOGGER').info("------------------ Test finished successfully ---------------------")
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
    
