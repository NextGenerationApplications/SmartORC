'''
Created on 11 feb 2021

@author: Luca Ferrucci
'''

from dynamic_orchestrator.core.abstract_orchestrator import AbstractOrchestrator
from numbers import Number
from mip import Model, xsum, BINARY, maximize, OptimizationStatus
from pickle import NONE
import yaml

class ConcreteOrchestrator(AbstractOrchestrator):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''               
        
    def component_requirements_translation(self,requirements):
        component_translation = {}
        for requirement_name, requirement_value in requirements.items():
            if requirement_name == 'os':
                if requirement_value == 'linux':
                    component_translation['Qos'] = 1
            if requirement_name == 'arch':
                if requirement_value == 'x86_64': 
                    component_translation['Qarch'] = 1
                elif requirement_value == 'ARM Cortex-A72':                  
                    component_translation['Qarch'] = 2
            if requirement_name == 'hardware_requirements':
                for hw_requirement_name, hw_requirement_value in requirements['hardware_requirements'].items(): 
                    if hw_requirement_name == 'cpu':
                        component_translation['hardware_requirements_cpu'] = int(hw_requirement_value)
                    if hw_requirement_name == 'ram':
                        component_translation['hardware_requirements_ram'] = int(hw_requirement_value)
                    if hw_requirement_name == 'disk':
                        component_translation['hardware_requirements_disk'] = int(hw_requirement_value)
                    if hw_requirement_name == 'gpu':
                        for gpu_requirement_name, gpu_requirement_value in requirements['hardware_requirements']['gpu'].items():
                            if gpu_requirement_name == 'model':
                                if gpu_requirement_value == 'NVIDIA GeForce RTX 20-series':
                                    component_translation['Qhardware_requirements_gpu_model'] = 1
                            if gpu_requirement_name == 'dedicated':
                                if gpu_requirement_value == 'True':
                                    component_translation['Qhardware_requirements_gpu_dedicated'] = 1
                                else:
                                    component_translation['Qhardware_requirements_gpu_dedicated'] = 0

                                   
        #f = open("C:\\Users\\Sara\\git\\dynamic-orchestrator\\appmodels\\AppModelFileID1\\AppModel.yml", "r")       
        #app_model = yaml.load(f)
        component_translation['links'] = None    
        return component_translation                      
                                                                  
    def generate_app_components_request_model(self, components, matchmaking_model):
        
        app_components_request_model = []
        
        application_component_instance_parts = components[0].component_name.rsplit('-',1)
        application_instance = application_component_instance_parts[0]
        for component in matchmaking_model[application_instance]:
            for application_component_instance_req in components:
                if application_component_instance_req.component_name == component['component']:
                    # Found the requirements of one the component to be deployed
                    app_components_request_model.append(self.component_requirements_translation(component['host']['requirements'])) 
        
         #   if application_instance[0] in matchmaking_model:
         #       component_list = matchmaking_model[application_instance[0]]
         #       for component in component_list:
         #           None                     
                
        return None
    
    def generate_federation_resource_availability_model(self,components, RID_response, matchmaking_model):
        return None
    
    def calculate_dep_plan(self, components, RID_response, matchmaking_model):
        """calculate_dep_plan
           matchmaking of components and ACCORDION federation resources will be done in this method
        :param components: 
        :type : array of dictionaries
        :param : RID_response
        :type : 
        :param : matchmaking_model
        :type : 
        :rtype: List[str] list of file names
                return a None List if there is an error during process 
        """
        App_Components_req = self.generate_app_components_request_model(components,matchmaking_model)
        Fed_res_availability = self.generate_federation_resource_availability_model(RID_response, matchmaking_model)
                
        # Construction of Python-MIP MILP problem
        
        MILP = Model()
        NumComponents = len(App_Components_req)
        NumEdgeMiniclouds = len(Fed_res_availability)
        
        # decision variables: decision_vars x(jn) with j in Components, n in EdgeMinicloud 
        decision_variables = [[MILP.add_var('x({},{})'.format(j, n), var_type=BINARY)
                            for j in range(NumComponents)] for n in range(NumEdgeMiniclouds)]

        # every application component MUST be deployed     
        #MILP += xsum(decision_variables[n][j] 
        #             for j in range(NumComponents) 
        #                for n in range(NumEdgeMiniclouds)) == NumComponents
        
        # every application component MUST be deployed on exactly an EdgeMinicloud
        for j in range(NumComponents):
            MILP += xsum(decision_variables[n][j]  for n in range(NumEdgeMiniclouds)) == 1
            
        # every dep plan must respect contraints on resource availability of every EdgeMinicloud
        for resource in Fed_res_availability[0]:
            if not (resource == 'links'): 
                if not (resource[0] == 'Q'):
                    n=0
                    for EdgeMinicloud in Fed_res_availability:     
                        MILP += xsum(((decision_variables[n][j])*((App_Components_req[j])[resource])) 
                                     for j in range(NumComponents) 
                                        if resource in (App_Components_req[j])) <= EdgeMinicloud[resource]
                        n+=1 
         
        # every dep plan must respect constraints on QoS indicators of every EdgeMinicloud
        for resource in Fed_res_availability[0]:
            if not (resource == 'links'): 
                if (resource[0] == 'Q'):
                    n=0
                    for EdgeMinicloud in Fed_res_availability:    
                        for j in range(NumComponents):
                            if resource in (App_Components_req[j]):
                                MILP += ((decision_variables[n][j])*((App_Components_req[j])[resource]) - EdgeMinicloud[resource]) <= 0
                                n+=1                                            
               
        # auxiliary decision variables: decision_vars y (ijn1n2) with i and j in Components with i!=j, n1 and n2 in EdgeMinicloud with n1!=n2 
        auxiliary_decision_variables = [[[[MILP.add_var('y({},{},{},{})'.format(i, j, n1, n2), var_type=BINARY)
                for i in range(NumComponents)] for j in range(NumComponents)] for n1 in range(NumEdgeMiniclouds)] for n2 in range(NumEdgeMiniclouds)]               
                              
        # every dep plan must respect contraints on resource availability of every link between components, 
        # for every network link between EdgeMinicloud, using auxiliary variables to linearize the constraint        
        for edge_resource in ((Fed_res_availability[0])['links'])[0]:
            if not (edge_resource[0] == 'Q'):
                n1=0
                for EdgeMinicloud in Fed_res_availability:
                    n2=0 
                    pos=0
                    while n2 < len(Fed_res_availability):                        
                        if not (n1 == n2):      
                            MILP += xsum(((auxiliary_decision_variables[n2][n1][j][i])*((((App_Components_req[i])['links'])[j])[edge_resource]))
                                     for i in range(NumComponents)
                                          for j in range(NumComponents) 
                                            if not (i==j) 
                                                if ((App_Components_req[i])['links']) 
                                                    if (j in ((App_Components_req[i])['links'])) 
                                                        if ((App_Components_req[i])['links'])[j] 
                                                            if (edge_resource in ((App_Components_req[i])['links'])[j])) <= ((EdgeMinicloud['links'])[pos])[edge_resource]
                            pos+=1
                        n2+=1
                    n1+=1            
  
        # every dep plan must respect contraints on QoS indicators of every link between components, 
        # for every network link between EdgeMinicloud, using auxiliary variables to linearize the constraint
        for edge_resource in ((Fed_res_availability[0])['links'])[0]:
            if (edge_resource[0] == 'Q'):
                n1=0
                for EdgeMinicloud in Fed_res_availability:
                    n2=0 
                    pos=0
                    while n2 < len(Fed_res_availability):                        
                        if not (n1 == n2):  
                            for i in range(NumComponents):
                                for j in range(NumComponents): 
                                    if not (i==j):   
                                        if ((App_Components_req[i])['links']): 
                                            if (j in ((App_Components_req[i])['links'])): 
                                                if ((App_Components_req[i])['links'])[j]:
                                                    if (edge_resource in ((App_Components_req[i])['links'])[j]):                                                         
                                                            MILP += ((auxiliary_decision_variables[n2][n1][j][i])*((((App_Components_req[i])['links'])[j])[edge_resource] - ((EdgeMinicloud['links'])[pos])[edge_resource])) <= 0
                            pos+=1                            
                        n2+=1
                    n1+=1  
                    
        #conditions to link auxiliary decision variable to main decision variables
        for i in range(NumComponents):
            for j in range(NumComponents): 
                if not (i==j):
                    for n1 in range(NumEdgeMiniclouds):
                            for n2 in range(NumEdgeMiniclouds):   
                                if not (n1==n2):                         
                                    MILP +=  (decision_variables[n1][i] + decision_variables[n2][j] - auxiliary_decision_variables[n2][n1][j][i]) <= 1
                                    MILP +=  (decision_variables[n1][i]/2 + decision_variables[n2][j]/2 - auxiliary_decision_variables[n2][n1][j][i]) >= 0

  
        
        # Maximize the availability of resources, except QoS indicators

        MILP.objective = maximize(xsum ((Fed_res_availability[n])[resource] -  
                                        xsum(((decision_variables[n][j])*((App_Components_req[j])[resource]))
                                               for j in range(NumComponents) 
                                                    if resource in (App_Components_req[j])) 
                                          for n in range(NumEdgeMiniclouds)
                                               for resource in Fed_res_availability[0]
                                                  if not (resource == 'links')
                                                    if not (resource[0] == 'Q')))     
         
        status = MILP.optimize()
        result_documents = []
        if status == OptimizationStatus.ERROR:
            return None    
        if status == OptimizationStatus.NO_SOLUTION_FOUND or status == OptimizationStatus.INFEASIBLE or status == OptimizationStatus.INT_INFEASIBLE or status == OptimizationStatus.UNBOUNDED:  
            return result_documents
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print('solution:')
            n=0
            for v in MILP.vars:
                if(v.name[0] == 'x'):
                    print('EdgeMinicloud: ', divmod(n,NumComponents)[0])
                    EdgeMinicloud = divmod(n,NumComponents)[0]
                    print('AppComponent: ', divmod(n,NumComponents)[1])                                                    
                    Appcomponent = divmod(n,NumComponents)[1]
                    if Appcomponent == 0:
                        result_documents.append([])
                    if v.x == 1:
                        result_documents[EdgeMinicloud].append(Appcomponent)          
                    print('{} : {}'.format(v.name, v.x))
                    n+=1 
        return result_documents       