'''
Created on 11 feb 2021

@author: Ferrucci
'''

from dynamic_orchestrator.core.abstract_orchestrator import AbstractOrchestrator

class ConcreteOrchestrator(AbstractOrchestrator):
    '''
    classdocs
    '''
    AppModelContent = None
    MonitorDataContent = None
    
    def __init__(self):
        '''
        Constructor
        '''   
    def AppModelContent_getter(self):
        return self.AppModelContent

    def MonitorDataContent_getter(self):
        return self.MonitorDataContent

    def calculate_dep_plan(self, AppModelContent, MonitorDataContent):
        """calculate_dep_plan

        :param AppModelContent: 
        :type AppModelContent: 
        :param MonitorDataContent: 
        :type MonitorDataContent: 

        :rtype: List[str] list of file names 
        """
        
        self.AppModelContent = AppModelContent
        self.MonitorDataContent = MonitorDataContent
        
        
        return  ['./test/AppModel.yml', './test/MonitorModel.yml'] 