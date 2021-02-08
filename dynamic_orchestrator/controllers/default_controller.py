from dynamic_orchestrator.controllers.app_model_controller import APPMODELS_PATH
from dynamic_orchestrator.controllers.monitor_data_controller import MONITORDATA_PATH
import os
import yaml
import flask
from requests_toolbelt import MultipartEncoder
from dynamic_orchestrator.core.orchestrator import calculate_dep_plan
 
def depplan_create(app_id, federation_id):  
    """depplan_create
    
    :param app_id: Application model Yaml file identifier
    :type app_id: str
    :param federation_id: MonitorData resources availabilit Yaml file identifier
    :type federation_id: str

    :rtype: List[InlineResponse2002]
    """ 
    filename = None
    try:
        AppModelFilePath = None
        AppModelFile = None
        if os.path.isdir(APPMODELS_PATH):
            AppModelsDirList = os.listdir(APPMODELS_PATH)
            if app_id in AppModelsDirList:
                directory =  os.path.join(APPMODELS_PATH,app_id)
                if os.path.isdir(directory):
                    AppModelsFileDirList = os.listdir(directory)
                    for filename in AppModelsFileDirList:
                        AppModelFilePath = os.path.join(directory,filename)
                        AppModelFile = open(AppModelFilePath,'rb')  
                else:
                    return {'message': 'A AppModel Yaml file not exists with the given identifier'}, 409
            else:
                return {'message': 'A AppModel Yaml file not exists with the given identifier'}, 409
        else:
            return {'message': 'A AppModel Yaml file not exists with the given identifier'}, 409
    except:
        return {'message': 'A AppModel Yaml file not exists with the given identifier or could not be opened'}, 409
    
    filename = None
    try:
        MonitorDataFilePath = None
        MonitorDataFile = None        
        if os.path.isdir(MONITORDATA_PATH):
            MonitorDataDirList = os.listdir(MONITORDATA_PATH)
            if federation_id in MonitorDataDirList:
                directory =  os.path.join(MONITORDATA_PATH,federation_id)
                if os.path.isdir(directory):
                    MonitorDataFileDirList = os.listdir(directory)
                    for filename in MonitorDataFileDirList:
                        MonitorDataFilePath = os.path.join(directory,filename)
                        MonitorDataFile = open(MonitorDataFilePath, 'rb')
                else:            
                    return {'message': 'A MonitorData Yaml file not exists with the given identifier'}, 409
            else:            
                return {'message': 'A MonitorData Yaml file not exists with the given identifier'}, 409
        else:            
            return {'message': 'A MonitorData Yaml file not exists with the given identifier'}, 409
    except:
        return {'message': 'A MonitorData Yaml file not exists with the given identifier  or could not be opened'}, 409

    AppModelContent = yaml.load(AppModelFile, Loader = yaml.FullLoader)
    MonitorDataContent = yaml.load(MonitorDataFile, Loader = yaml.FullLoader)
    
    #Elaboration of the Deploy plan
    FileResponseList = calculate_dep_plan(AppModelContent, MonitorDataContent)
    fields = {}
    key = 'file'
    i = 1
    for File in FileResponseList:
        FileOpened = (File, open(File, 'rb'), 'text/plain')
        fields[key+str(i)] = FileOpened
        i=i+1
        
    m = MultipartEncoder(fields)
    return flask.Response(m.to_string(), mimetype=m.content_type),200