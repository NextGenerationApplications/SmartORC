'''
Created on 5 lug 2021

@author: Ferrucci
'''
import threading
from converter_package.Converter import tosca_to_k8s  
import yaml
from requests_toolbelt import MultipartEncoder
import requests
from datetime import datetime
import json

class vim_sender_worker(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self, logger, thread_id, app_instance, nodelist, imagelist, namespace_yaml, secret_yaml, EdgeMinicloud, components, vim_results, minicloud_ip):
        threading.Thread.__init__(self)
        self.app_instance = app_instance
        self.nodelist = nodelist
        self.imagelist = imagelist
        self.namespace_yaml = namespace_yaml[app_instance]
        self.secret_yaml = secret_yaml[app_instance]
        self.EdgeMinicloud = EdgeMinicloud
        self.components = components
        self.thread_id = thread_id
        self.vim_results = vim_results
        self.logger = logger
        self.minicloud_ip = minicloud_ip
        
    def calculate_pers_files_list(self,deployment_file):
        pers_f_list = []  
        spec1 = deployment_file.get('spec')
        if spec1:
            template = spec1.get('template')
            if template:
                spec2 = template.get('spec')
                if spec2:
                    volumes = spec2.get('volumes')
                    if volumes:
                        for volume in volumes:
                            pvc =  volume.get('persistentVolumeClaim')
                            if pvc:
                                pvc_name = pvc.get('claimName')
                                if pvc_name:
                                    pers_f_list.append(pvc_name)
        return pers_f_list
        
      
    def run(self):
        
        self.logger.info("Thread " + str(self.thread_id) + " started to deploy following components on EdgeMinicloud %s :" % self.EdgeMinicloud)
        for i in range(len(self.components)):
            self.logger.info("--- Component:  %s " % self.components[i])

        try:
            yaml_files_list = [self.namespace_yaml, self.secret_yaml]
            
            
            self.logger.info("Thread " + str(self.thread_id) + ": Request to Converter for App instance %s: K3S configuration files generation function invoked" % self.app_instance)        
            deployment_files, persistent_files, service_files = tosca_to_k8s(
                self.nodelist, 
                self.imagelist, 
                self.app_instance, 
                self.EdgeMinicloud, 
                self.minicloud_ip,
                []# list of dict {"comp_name":gpu model} GPUs required by the application,. empty list if not required
            )

            print ("Converter response: \n")
            print ("\tDeployment files:", deployment_files)
            print ("\tPersistent files:", persistent_files)
            print ("\tService files", service_files)
            
            for component in self.components:
                componentEMC = component + '-' + self.EdgeMinicloud
                for deployment_component in deployment_files:
                    deployment_file = deployment_component.get(componentEMC)
                    if deployment_file:
                        persistent_files_list = self.calculate_pers_files_list(deployment_file)
                        yaml_files_list.append(deployment_file) 
                        for pers_file_name in persistent_files_list:
                            for pers_file_record in persistent_files:
                                pers_file = pers_file_record.get(pers_file_name)  
                                if pers_file:
                                    yaml_files_list.append(pers_file)  
                for service in service_files:
                    for service_name, service_desc in service.items():
                        if componentEMC in service_name:
                            yaml_files_list.append(service_desc)
    
            yaml_file = yaml.dump_all(yaml_files_list)  
               
            self.logger.debug("Thread " + str(self.thread_id) + ": K3S configuration file content")
            self.logger.debug("Thread " + str(self.thread_id) + ": %s" % yaml_file)
                          
            vim_request = MultipartEncoder(fields={'operation': 'deploy', 'minicloud_id': self.EdgeMinicloud, 'file': (component, yaml_file, 'text/plain')})  
        
            vim_response = requests.post("http://continuum.accordion-project.eu:5000/VIM/request", timeout=10, data=vim_request,
                              headers={'Content-Type': vim_request.content_type})
            vim_response.raise_for_status()
            self.logger.debug("Thread " + str(self.thread_id) + ": Request to VimGw returned with response: %s" % vim_response.text)

            vim_result = vim_response.json()
            
            result = []
            for component in self.components:
                component_name = component + '-' + self.EdgeMinicloud
                result.append({component_name: int(datetime.today().timestamp())}) 
            self.vim_results[self.thread_id] = result

            
        except requests.exceptions.Timeout as err:
            error = 'Deploy operation not executed successfully due to a timeout in the communication with the Vim of the EdgeMinicloud with id:  ' + self.EdgeMinicloud
            result = []
            for component in self.components:
                component_name = component + '-' + self.EdgeMinicloud
                result.append({component_name: error}) 
            self.vim_results[self.thread_id] = result
            
        except requests.exceptions.RequestException as err:
            error = 'Deploy operation not executed successfully due to the following internal server error in the communication with the Vim of the EdgeMinicloud with id:  ' + self.EdgeMinicloud + ": " + str(err)
            result = []
            for component in self.components:
                component_name = component + '-' + self.EdgeMinicloud
                result.append({component_name: error}) 
            self.vim_results[self.thread_id] = result    
            
        except OSError as err:
            if err:
                error = '1 Deploy operation not executed successfully due to the following internal server error: ' + err.strerror
            else:
                error = '2 Deploy operation not executed successfully due to an unknown internal server error! ' + err
            result = []
            for component in self.components:
                component_name = component + '-' + self.EdgeMinicloud
                result.append({component_name: error}) 
            self.vim_results[self.thread_id] = result        
            
        except Exception as e:
            error = '3 Deploy operation not executed successfully due to an unknown internal server error!' + e
            result = []
            for component in self.components:
                component_name = component + '-' + self.EdgeMinicloud
                result.append({component_name: error}) 
            self.vim_results[self.thread_id] = result        
