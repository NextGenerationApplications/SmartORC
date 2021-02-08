'''
Created on 8 feb 2021

@author: Ferrucci
'''
        
def calculate_dep_plan(AppModelContent, MonitorDataContent):
    """calculate_dep_plan

    :param AppModelContent: 
    :type AppModelContent: 
    :param MonitorDataContent: 
    :type MonitorDataContent: 

    :rtype: List[str] list of file names 
    """
    
    #Change the path to the right one to create the Docker container
    return ['./test/ProvaAppModel.yml', './test/ProvaMonitorModel.yml'] 
        