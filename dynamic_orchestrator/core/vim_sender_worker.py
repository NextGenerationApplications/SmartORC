'''
Created on 5 lug 2021

@author: Ferrucci
'''
import threading
import yaml
import requests
import json
import traceback

from requests_toolbelt import MultipartEncoder
from datetime import datetime

from converter_package.Converter import tosca_to_k8s, ID, scale_out_to_k8s



class vim_sender_worker(threading.Thread):
    '''
    classdocs
    '''
    def __init__(self, logger, thread_id, ns, componentInfo, inter_app_model, nodelist, imagelist, namespace_yaml, 
    secret_yaml, EdgeMinicloud, components, vim_results, minicloud_ip, local_scaleout):
        threading.Thread.__init__(self)
        self.ns = ns # ACCORDION namespace (for a component, so only application data would be ok if having multiple components. be aware.)
        self.componentInfo = componentInfo
        self.inter_app_model = inter_app_model
        self.nodelist = nodelist
        self.imagelist = imagelist
        self.namespace_yaml = namespace_yaml
        self.secret_yaml = secret_yaml
        self.EdgeMinicloud = EdgeMinicloud
        self.components = components
        self.thread_id = thread_id
        self.vim_results = vim_results
        self.logger = logger
        self.minicloud_ip = minicloud_ip
        self.local_scaleout = local_scaleout
        
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

            yaml_files_list = []
            persistent_files = []
            service_files = []

            if (self.local_scaleout):
                deployment_files = [scale_out_to_k8s(self.componentInfo, self.inter_app_model)]
            else:

                yaml_files_list = [self.namespace_yaml, self.secret_yaml]
                #self.logger.info("Thread " + str(self.thread_id) + ": Request to Converter for App instance %s: K3S configuration files generation function invoked" % self.app_instance)        
                deployment_files, persistent_files, service_files = tosca_to_k8s(
                    self.nodelist, 
                    self.imagelist, 
                    ID.generate_k3s_namespace(self.ns['appName'], self.ns['appVersion'], self.ns['appInstanceId']),
                    self.EdgeMinicloud, 
                    self.minicloud_ip,
                    [{'component': self.componentInfo, 'gpu_model': "nvidia.com/TU117_GEFORCE_GTX_1650"}]# list of dict {"comp_name":gpu model} GPUs in the minciloud. empty list if not required
                )


            # contacting the ACES to prepare for the remote image if any
            aces_url = 'http://'+self.minicloud_ip+':2022/yaml'
            print ("Sending request to ACES at: "+aces_url)
            # aces_response = requests.post('http://'+self.minicloud_ip+':2022/yaml')
            # print(aces_response.content)

            # preparing to send to vimgw
            print ("Files sent to VIMGW: \n")
            print ("\tDeployment files:", deployment_files)
            print ("\tPersistent files:", persistent_files)
            print ("\tService files", service_files)
            
            for component in self.components:
                # manage deployment files
                for deployment_item in deployment_files:
                    if component in list(deployment_item.keys())[0].lower():
                        # we found a matching between component and deployment file
                        deployment_file = list(deployment_item.values())[0]
                        yaml_files_list.append(deployment_file) 
                        # manage the persistent files
                        persistent_files_list = self.calculate_pers_files_list(deployment_file)
                        for pers_file_name in persistent_files_list:
                            for pers_file_record in persistent_files:
                                pers_file = pers_file_record.get(pers_file_name)  
                                if pers_file:
                                    yaml_files_list.append(pers_file)  
                # manage service files                    
                for service_item in service_files:
                        if component in list(service_item.keys())[0].lower():
                            yaml_files_list.append(list(service_item.values())[0])
    
            yaml_file = yaml.dump_all(yaml_files_list)  


            ## DEBUG for OVR use case
            #replacement = "acc-ovrxnrh-0-0-7-thwfq"
            #replaced = self.ns['appInstanceInfo']
            #self.logger.debug("Replacing "+replaced + " with "+replacement)
            #yaml_file = yaml_file.replace(replaced, replacement)
            # ----- end debug
               
            self.logger.debug("Thread " + str(self.thread_id) + ": K3S configuration file content")
            self.logger.debug("Thread " + str(self.thread_id) + ": %s" % yaml_file)
                          
            vim_request = MultipartEncoder(fields={'operation': 'deploy', 'minicloud_id': self.EdgeMinicloud, 'file': (component, yaml_file, 'text/plain')})  
        
            # url = "http://continuum.accordion-project.eu:5000/VIM/request"
            url = "http://vimgw:5000/VIM/request"

            vim_response = requests.post(url, timeout=10, data=vim_request,
                              headers={'Content-Type': vim_request.content_type})
            vim_response.raise_for_status()
            self.logger.debug("Thread " + str(self.thread_id) + ": Request to VimGw returned with response: %s" % vim_response.text)

            vim_result = vim_response.json()
            
            result = []
            for component in self.components:
                component_name = component + '-' + self.EdgeMinicloud
                result.append({component_name: int(datetime.today().timestamp())}) 
            self.vim_results[self.thread_id] = result

        except Exception as e:
            self.logger.info(f"Exception in thread {self.thread_id}: {e}")
            traceback.print_exc()

            # result = []
            # for component in self.components:
            #     component_name = component + '-' + self.EdgeMinicloud
            #     result.append({component_name: error}) 
            # self.vim_results[self.thread_id] = result    
        
            
    
