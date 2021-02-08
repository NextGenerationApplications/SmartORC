from dynamic_orchestrator.models.inline_response2001 import InlineResponse2001  
from werkzeug.utils import secure_filename
import os
import shutil

MONITORDATA_PATH = './monitordata'

def monitordata_create(body, file): 
    """monitordata_create

    :param app_id: 
    :type app_id: str
    :param file: 
    :type file: strstr

    :rtype: None
    """
    global MONITORDATA_PATH
    file_directory = os.path.join(MONITORDATA_PATH, body.get('federation_id'))
    try:
        os.makedirs(file_directory)
    except:
        return {'message': 'Not created. A MonitorData Yaml file already exists with the given identifier. Use PUT to update it'}, 409 

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(file_directory, filename)
        file.save(filepath)
    except:
        return {'message': 'Failed to create MonitorData Yaml file with the given name and identifier'}, 500 
    return  {'message': 'MonitorData Yaml file created successfully !'}, 200

def monitordata_delete(federation_id):  # noqa: E501
    """monitordata_delete

     # noqa: E501

    :param federation_id: 
    :type federation_id: str

    :rtype: None
    """
    global MONITORDATA_PATH
    try:
        if os.path.isdir(MONITORDATA_PATH):
            AppModelsDirList = os.listdir(MONITORDATA_PATH)
            if federation_id in AppModelsDirList:             
                directory =  os.path.join(MONITORDATA_PATH,federation_id)
                if os.path.isdir(directory):                    
                    shutil.rmtree(directory)
                else:
                    return{'message': 'A MonitorData Yaml file not exists with the given identifier'},409
            else:
                return{'message': 'A MonitorData Yaml file not exists with the given identifier'},409
        else:
            return{'message': 'A MonitorData Yaml file not exists with the given identifier'},409
    except:
        return {'message': 'MonitorData to delete MonitorData Yaml file with the given identifier'}, 500    
    return {'message':'MonitorData Yaml file with the given identifier deleted succesfully'}, 200

def monitordata_read_all():  # noqa: E501
    """monitordata_read_all

    Return the list of the name of Yaml files that contains the availability of resources of an entire federation and the respective identifiers 


    :rtype: List[InlineResponse2001]
    """
    global MONITORDATA_PATH 
    response = [] 
    if os.path.isdir(MONITORDATA_PATH):
        DataMonitorDirList = os.listdir(MONITORDATA_PATH)
        for federation_id in DataMonitorDirList:
            directory =  os.path.join(MONITORDATA_PATH,federation_id)
            if os.path.isdir(directory):
                DataMonitorFileDirList = os.listdir(directory)
                for filename in DataMonitorFileDirList:
                    response_el=InlineResponse2001(filename,federation_id)
                    response.append(response_el)                                  
    return response, 200

def monitordata_update(federation_id, body):  # noqa: E501
    """monitordata_update

     # noqa: E501

    :param body: Substitute a Yaml file that contains the representation of the availability of resources of an entire federation with the given identifier with the new file passed as a parameter
    :type body: dict | bytes
    :param federation_id: 
    :type federation_id: str

    :rtype: None
    """
    global MONITORDATA_PATH
    file_directory = os.path.join(MONITORDATA_PATH,federation_id)
    try:
        if os.path.isdir(file_directory):
            FedIDDirList = os.listdir(file_directory)
            for filename in FedIDDirList:
                filepath = os.path.join(file_directory,filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)     
                else:
                    return {'message': 'Failed to update MonitorData Yaml file with the given identifier: an Yaml file with the given identifier does not exist. Use POST to create it'}, 409  
        else:
            return {'message': 'Failed to update MonitorData Yaml file with the given identifier: an Yaml file with the given identifier does not exist. Use POST to create it'}, 409
        filename = secure_filename(body.filename)
        body.save(os.path.join(file_directory, filename))
    except:
        return {'message': 'Failed to update the MonitorData Yaml file with the new one with the given name and identifier'}, 500 
    return  {'message': 'MonitorData Yaml file updated successfully !'}, 200