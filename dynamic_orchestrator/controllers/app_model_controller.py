from dynamic_orchestrator.models.inline_response200 import InlineResponse200  # noqa: E501
from werkzeug.utils import secure_filename
import os
import shutil
from flask import current_app

APPMODELS_PATH = '/appmodels'

def appmodels_basepath():
    global APPMODELS_PATH
    return current_app.config.get('UPLOAD_FOLDER') + APPMODELS_PATH

def appmodel_create(body,file):  
    """appmodel_create

    :param app_id: 
    :type app_id: str
    :param file: 
    :type file: str

    :rtype: None
    """

    file_directory = os.path.join(appmodels_basepath(), body.get('app_id'))
    try:
        os.makedirs(file_directory)
    except:
        return {'message': 'Not created. A AppModel Yaml file already exists with the given identifier. Use PUT to update it'}, 409 

    filepath = os.path.join(file_directory, file.filename)
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(file_directory, filename)
        file.save(filepath)
    except:
        return {'message': 'Failed to create AppModel Yaml file with the given name and identifier'}, 500 
    return  {'message': 'AppModel Yaml file created successfully !'}, 200

def appmodel_delete(app_id):  
    """appmodel_delete

     # noqa: E501

    :param app_id: 
    :type app_id: str

    :rtype: None
    """
    try:
        if os.path.isdir(appmodels_basepath()):
            AppModelsDirList = os.listdir(appmodels_basepath())
            if app_id in AppModelsDirList:             
                directory =  os.path.join(appmodels_basepath(),app_id)
                if os.path.isdir(directory):
                    shutil.rmtree(directory)
                else:
                    return{'message': 'A AppModel Yaml file does not exist with the given identifier'},409
            else:
                return{'message': 'A AppModel Yaml file does not exist with the given identifier'},409
        else:
            return{'message': 'A AppModel Yaml file does not exist with the given identifier'},409
    except:
        return {'message': 'Failed to delete AppModel Yaml file with the given identifier'}, 500    
    return {'message':'AppModel Yaml file with the given identifier deleted succesfully'}, 200

def appmodel_read_all():  
    """appmodel_read_all

    Return the list of the name of Yaml files that contains the representation of the model of the applications submitted until now and the respective identifiers # noqa: E501

    :rtype: List[InlineResponse200]
    """
    response = [] 
    if os.path.isdir(appmodels_basepath()):
        AppModelsDirList = os.listdir(appmodels_basepath())
        for app_id in AppModelsDirList:
            directory =  os.path.join(appmodels_basepath(),app_id)
            if os.path.isdir(directory):
                AppModelsFileDirList = os.listdir(directory)
                for filename in AppModelsFileDirList:
                    response_el=InlineResponse200(filename,app_id)
                    response.append(response_el)                                  
    return response, 200

def appmodel_update(app_id,file):  
    """appmodel_update

     # noqa: E501

    :param file: Substitute the Yaml file that contains the representation of the model of the application with the given identifier with the new file passed as a parameter
    :type file: dict | bytes
    :param app_id: 
    :type app_id: str

    :rtype: None
    """
    global APPMODELS_PATH
    file_directory = os.path.join(appmodels_basepath(),app_id)
    try:
        if os.path.isdir(file_directory):
            AppIDDirList = os.listdir(file_directory)
            for filename in AppIDDirList:
                filepath = os.path.join(file_directory,filename)
                if os.path.isfile(filepath):                    
                    os.remove(filepath)     
                else:
                    return {'message': 'Failed to update AppModel Yaml file with the given identifier: an Yaml file with the given identifier does not exist. Use POST to create it'}, 409          
        else:
            return {'message': 'Failed to update AppModel Yaml file with the given identifier: an Yaml file with the given identifier does not exist. Use POST to create it'}, 409 
        filename = secure_filename(file.filename)
        file.save(os.path.join(file_directory, file.filename))
    except:
        return {'message': 'Failed to update the AppModel Yaml file with the new one with the given name and identifier'}, 500 
    return  {'message': 'AppModel Yaml file updated successfully !'}, 200
