'''
Created on 5 lug 2021

@author: Ferrucci
'''
import threading
from dynamic_orchestrator.converter.Converter import tosca_to_k8s  
import yaml
import requests

class vim_sender_worker(threading.Thread):
    '''
    classdocs
    '''

    def __init__(self, app_instance, nodelist, imagelist, namespace_yaml, secret_yaml, EdgeMinicloud, components, vim_component_ids):
        threading.Thread.__init__(self)
        self.app_instance = app_instance
        self.nodelist = nodelist
        self.imagelist = imagelist
        self.namespace_yaml = namespace_yaml[app_instance]
        self.secret_yaml = secret_yaml[app_instance]
        self.EdgeMinicloud = EdgeMinicloud
        self.components = components
        self.vim_component_ids = vim_component_ids
      
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
        yaml_files_list = [self.namespace_yaml, self.secret_yaml]
        
        deployment_files, persistent_files, service_files = tosca_to_k8s(self.nodelist, self.imagelist, self.app_instance, self.EdgeMinicloud)

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
                      
        m1 = MultipartEncoder(fields={'operation': 'deploy', 'file': (component, yaml_file, 'text/plain')})  
        
        r1 = requests.post("http://localhost:5000/VIM/request", data=m1,
                          headers={'Content-Type': m1.content_type})
            
                
        