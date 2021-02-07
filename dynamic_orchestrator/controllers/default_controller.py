import connexion
import six

from dynamic_orchestrator.controllers.app_model_controller import APPMODELS_PATH
from dynamic_orchestrator.controllers.monitor_data_controller import MONITORDATA_PATH
from flask import current_app
from dynamic_orchestrator import util
import os
import yaml
from flask.helpers import send_file

def depplan_create(app_id, federation_id):  
    """depplan_create
    
    :param app_id: Application model Yaml file identifier
    :type app_id: str
    :param federation_id: MonitorData resources availabilit Yaml file identifier
    :type federation_id: str

    :rtype: str
    """
    try:
        AppModelFile = None
        if os.path.isdir(APPMODELS_PATH):
            AppModelsDirList = os.listdir(APPMODELS_PATH)
            if app_id in AppModelsDirList:
                directory =  os.path.join(APPMODELS_PATH,app_id)
                if os.path.isdir(directory):
                    AppModelsFileDirList = os.listdir(directory)
                    for filename in AppModelsFileDirList:
                        AppModelFile = open(os.path.join(directory,filename), 'rb')  
    except OSError:
        return {'message': 'A AppModel Yaml file not exists with the given identifier'}, 409
    
    try:
        MonitorDataFile = None        
        if os.path.isdir(MONITORDATA_PATH):
            MonitorDataDirList = os.listdir(MONITORDATA_PATH)
            if federation_id in MonitorDataDirList:
                directory =  os.path.join(MONITORDATA_PATH,federation_id)
                if os.path.isdir(directory):
                    MonitorDataFileDirList = os.listdir(directory)
                    for filename in MonitorDataFileDirList:
                        MonitorDataFile = open(os.path.join(directory,filename), 'rb')
    except OSError:
        return {'message': 'A MonitorData Yaml file not exists with the given identifier'}, 409
                         

    AppModelContent = yaml.load(AppModelFile, Loader = yaml.FullLoader)
    MonitorDataContent = yaml.load(MonitorDataFile, Loader = yaml.FullLoader)
    print(AppModelContent)
    print(MonitorDataContent)
    
    #Elaboration of the Deploy plan
    
    return send_file(os.path.join(directory,filename)),200 
    
    
