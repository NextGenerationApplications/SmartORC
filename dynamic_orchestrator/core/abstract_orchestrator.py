'''
Created on 8th february 2021

@author: Ferrucci
'''
    
from abc import ABCMeta, abstractmethod

class AbstractOrchestrator(metaclass=ABCMeta):

    @abstractmethod
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
        return   



        