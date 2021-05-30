'''
Created on 11 feb 2021

@author: Luca Ferrucci
'''

from dynamic_orchestrator.core.abstract_orchestrator import AbstractOrchestrator
from numbers import Number
from mip import Model, xsum, BINARY, maximize, OptimizationStatus

class ConcreteOrchestrator(AbstractOrchestrator):
    '''
    classdocs
    '''
    AppModelContent = None
    MonitorDataContent = None
#    resources = []
#    edge_resources = []
#    QOS_resources = []
#    QOS_edge_resources = []
    
    def __init__(self):
        '''
        Constructor
        '''   
    def AppModelContent_getter(self):
        return self.AppModelContent

    def MonitorDataContent_getter(self):
        return self.MonitorDataContent

    def checkAppModelFile(self,AppModelContent):
        """checkAppModelFile
        parsing of the AppModel file content
        :param AppModelContent 

        :rtype: True if the file has the correct syntax, false otherwise 
        """
              
        if not isinstance(AppModelContent, list):
            return False 
        NumberOfAppComponents = len(AppModelContent)
        if NumberOfAppComponents == 0:
            return False
        position = 0
        for AppComponent in AppModelContent:
            if not isinstance(AppComponent,dict):
                return False
            links_not_found = True
            for resource_type_req, resource_quantity_req in AppComponent.items():
                if not isinstance(resource_type_req,str):
                    return False 
                if resource_type_req == 'links':
                    AppComponentsEdges = resource_quantity_req
                    links_not_found = False
                    if isinstance(AppComponentsEdges,dict):
                        for edge_position, edge_resources_type_req in AppComponentsEdges.items():
                            if not isinstance (edge_position, int):
                                return False
                            if (0 > edge_position >= NumberOfAppComponents) or (edge_position == position):
                                return False
                            if not isinstance(edge_resources_type_req,dict):
                                return False 
                            if not edge_resources_type_req:
                                return False
                            for edge_resource_type_req, edge_resource_quantity_req in edge_resources_type_req.items(): 
                                if not isinstance(edge_resource_type_req,str):
                                    return False 
                                if not isinstance (edge_resource_quantity_req, Number):
                                    return False                                           
                else:
                    if (not resource_type_req in self.MonitorDataContent[0]):
                        return False
                    if not isinstance (resource_quantity_req, Number):
                        return False    
            if links_not_found:
                return False
            position+=1
        return True 
            
    def checkMonitorDataFile(self,MonitorDataContent):
        """checkMonitorDataFile
        parsing of the MonitorData file content
        :param MonitorDataContent 

        :rtype: True if the file has the correct syntax, false otherwise 
        """

        if not isinstance(MonitorDataContent, list):
            return False 
        NumberOfEdgeMiniclouds = len(MonitorDataContent)
        if NumberOfEdgeMiniclouds == 0:
            return False
        resources = MonitorDataContent[0]       
        edge_resources = ()
        if len(resources) == 0:
            return False
        for EdgeMinicloud in MonitorDataContent:
            if not isinstance(EdgeMinicloud,dict):
                return False
            links_not_found = True
            if not (len(resources) == len(EdgeMinicloud)):
                return False
            for resource, resource_quantity in EdgeMinicloud.items():
                if not isinstance(resource,str):
                    return False
                if resource == 'links':
                    EdgeMinicloudEdges = resource_quantity
                    links_not_found = False
                    if not isinstance(EdgeMinicloudEdges,list):
                        return False 
                    if not (len(EdgeMinicloudEdges) == (len(MonitorDataContent)-1)):
                        return False
                    edge_resources = EdgeMinicloudEdges[0]
                    for actual_edge_resources in EdgeMinicloudEdges:
                        if not isinstance(actual_edge_resources,dict):
                            return False  
                        if not len(edge_resources) == len(actual_edge_resources):
                            return False
                        for edge_resource, edge_resource_quantity in edge_resources.items():
                            if not isinstance(edge_resource,str):
                                return False
                            if not edge_resource in edge_resources:
                                return False
                            if not isinstance (edge_resource_quantity, Number):
                                return False    
                else:
                    if not resource in resources:
                        return None
                    if not isinstance (resource_quantity, Number):
                        return None                                       
            if links_not_found:
                return None
        return True
                
    def calculate_dep_plan(self, AppModelContent, MonitorDataContent):
        """calculate_dep_plan
           parsing of the AppModel and MonitorData must be done in this method
        :param AppModelContent: 
        :type AppModelContent: 
        :param MonitorDataContent: 
        :type MonitorDataContent: 

        :rtype: List[str] list of file names
                return a None List if there is an error during process 
        """
      
        self.AppModelContent = AppModelContent
        self.MonitorDataContent = MonitorDataContent
        
        if not self.checkMonitorDataFile(MonitorDataContent):
            return None
        if not self.checkAppModelFile(AppModelContent):                 
            return None
        
        # Construction of Python-MIP MILP problem
        
        MILP = Model()
        NumComponents = len(AppModelContent)
        NumEdgeMiniclouds = len(MonitorDataContent)
        
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
        for resource in MonitorDataContent[0]:
            if not (resource == 'links'): 
                if not (resource[0] == 'Q'):
                    n=0
                    for EdgeMinicloud in MonitorDataContent:     
                        MILP += xsum(((decision_variables[n][j])*((AppModelContent[j])[resource])) 
                                     for j in range(NumComponents) 
                                        if resource in (AppModelContent[j])) <= EdgeMinicloud[resource]
                        n+=1 
         
        # every dep plan must respect constraints on QoS indicators of every EdgeMinicloud
        for resource in MonitorDataContent[0]:
            if not (resource == 'links'): 
                if (resource[0] == 'Q'):
                    n=0
                    for EdgeMinicloud in MonitorDataContent:    
                        for j in range(NumComponents):
                            if resource in (AppModelContent[j]):
                                MILP += ((decision_variables[n][j])*((AppModelContent[j])[resource]) - EdgeMinicloud[resource]) <= 0
                                n+=1                                            
               
        # auxiliary decision variables: decision_vars y (ijn1n2) with i and j in Components with i!=j, n1 and n2 in EdgeMinicloud with n1!=n2 
        auxiliary_decision_variables = [[[[MILP.add_var('y({},{},{},{})'.format(i, j, n1, n2), var_type=BINARY)
                for i in range(NumComponents)] for j in range(NumComponents)] for n1 in range(NumEdgeMiniclouds)] for n2 in range(NumEdgeMiniclouds)]               
                              
        # every dep plan must respect contraints on resource availability of every link between components, 
        # for every network link between EdgeMinicloud, using auxiliary variables to linearize the constraint        
        for edge_resource in ((MonitorDataContent[0])['links'])[0]:
            if not (edge_resource[0] == 'Q'):
                n1=0
                for EdgeMinicloud in MonitorDataContent:
                    n2=0 
                    pos=0
                    while n2 < len(MonitorDataContent):                        
                        if not (n1 == n2):      
                            MILP += xsum(((auxiliary_decision_variables[n2][n1][j][i])*((((AppModelContent[i])['links'])[j])[edge_resource]))
                                     for i in range(NumComponents)
                                          for j in range(NumComponents) 
                                            if not (i==j) 
                                                if ((AppModelContent[i])['links']) 
                                                    if (j in ((AppModelContent[i])['links'])) 
                                                        if ((AppModelContent[i])['links'])[j] 
                                                            if (edge_resource in ((AppModelContent[i])['links'])[j])) <= ((EdgeMinicloud['links'])[pos])[edge_resource]
                            pos+=1
                        n2+=1
                    n1+=1            
  
        # every dep plan must respect contraints on QoS indicators of every link between components, 
        # for every network link between EdgeMinicloud, using auxiliary variables to linearize the constraint
        for edge_resource in ((MonitorDataContent[0])['links'])[0]:
            if (edge_resource[0] == 'Q'):
                n1=0
                for EdgeMinicloud in MonitorDataContent:
                    n2=0 
                    pos=0
                    while n2 < len(MonitorDataContent):                        
                        if not (n1 == n2):  
                            for i in range(NumComponents):
                                for j in range(NumComponents): 
                                    if not (i==j):   
                                        if ((AppModelContent[i])['links']): 
                                            if (j in ((AppModelContent[i])['links'])): 
                                                if ((AppModelContent[i])['links'])[j]:
                                                    if (edge_resource in ((AppModelContent[i])['links'])[j]):                                                         
                                                            MILP += ((auxiliary_decision_variables[n2][n1][j][i])*((((AppModelContent[i])['links'])[j])[edge_resource] - ((EdgeMinicloud['links'])[pos])[edge_resource])) <= 0
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

        MILP.objective = maximize(xsum ((MonitorDataContent[n])[resource] -  
                                        xsum(((decision_variables[n][j])*((AppModelContent[j])[resource]))
                                               for j in range(NumComponents) 
                                                    if resource in (AppModelContent[j])) 
                                          for n in range(NumEdgeMiniclouds)
                                               for resource in MonitorDataContent[0]
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