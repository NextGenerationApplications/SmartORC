from dynamic_orchestrator.controllers.app_model_controller import appmodels_basepath
from dynamic_orchestrator.controllers.monitor_data_controller import monitordata_basepath
import os,yaml,flask
from requests_toolbelt import MultipartEncoder
from flask import current_app

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
        if os.path.isdir(appmodels_basepath()):
            AppModelsDirList = os.listdir(appmodels_basepath())
            if app_id in AppModelsDirList:
                directory =  os.path.join(appmodels_basepath(),app_id)
                if os.path.isdir(directory):
                    AppModelsFileDirList = os.listdir(directory)
                    if not AppModelsFileDirList:
                        return {'message': 'A AppModel Yaml file does not exist with the given identifier'}, 409 
                    for filename in AppModelsFileDirList:
                        AppModelFilePath = os.path.join(directory,filename)
                        AppModelFile = open(AppModelFilePath,'rb')  
                else:
                    return {'message': 'A AppModel Yaml file does not exist with the given identifier'}, 409
            else:
                return {'message': 'A AppModel Yaml file does not exist with the given identifier'}, 409
        else:
            return {'message': 'A AppModel Yaml file does not exist with the given identifier'}, 409
    except:
        return {'message': 'A AppModel Yaml file does not exist with the given identifier'}, 409
    
    filename = None
    try:
        MonitorDataFilePath = None
        MonitorDataFile = None        
        if os.path.isdir(monitordata_basepath()):
            MonitorDataDirList = os.listdir(monitordata_basepath())
            if federation_id in MonitorDataDirList:
                directory =  os.path.join(monitordata_basepath(),federation_id)
                if os.path.isdir(directory):
                    MonitorDataFileDirList = os.listdir(directory)
                    if not MonitorDataFileDirList:
                        return {'message': 'A MonitorData Yaml file does not exist with the given identifier'}, 409 
                    for filename in MonitorDataFileDirList:
                        MonitorDataFilePath = os.path.join(directory,filename)
                        MonitorDataFile = open(MonitorDataFilePath, 'rb')
                else:            
                    return {'message': 'A MonitorData Yaml file does not exist with the given identifier'}, 409
            else:            
                return {'message': 'A MonitorData Yaml file does not exist with the given identifier'}, 409
        else:            
            return {'message': 'A MonitorData Yaml file does not exist with the given identifier'}, 409
    except:
        return {'message': 'A MonitorData Yaml file does not exist with the given identifier'}, 409
    try:
        MonitorDataContent = yaml.load(MonitorDataFile, Loader = yaml.FullLoader)
    except:
        return {'message': 'The AppModel Yaml file with the given identifier is not in a correct Yaml format. Use PUT to update it'}, 409
    
    try:
        AppModelContent = yaml.load(AppModelFile, Loader = yaml.FullLoader)
    except:
        return {'message': 'The MonitorData Yaml file with the given identifier is not in a correct Yaml format. Use PUT to update it'}, 409

    AppModelFile.close()
    MonitorDataFile.close()

    #Elaboration of the Deploy plan
    DocumentResponseList = current_app.config['ORCHESTRATOR'].calculate_dep_plan(AppModelContent, MonitorDataContent)
    
    if DocumentResponseList is None:
        return {'message': 'Internal error during calculus or parsing of files. Use PUT to update Yaml files'}, 409

    key = 'res'
    i = 1
    fields = {}
    if not DocumentResponseList:
        return {'message': 'Unfeasible or unbound or no solution found'}, 200
    for document in DocumentResponseList:
        if document:
            fields[key+str(i)] = yaml.dump(document)
        i+=1  
            
    m = MultipartEncoder(fields)
    return flask.Response(m.to_string(), mimetype=m.content_type),200