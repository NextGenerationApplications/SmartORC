from dynamic_orchestrator.models.inline_response200 import InlineResponse200  # noqa: E501
from werkzeug.utils import secure_filename
import os
import shutil
from flask import current_app
import requests
from dynamic_orchestrator.converter.Parser import ReadFile
from dynamic_orchestrator.converter.Converter import namespace,secret_generation  
from  urllib.error import HTTPError
from kubernetes import client, config, utils
import base64
import json
import yaml

APPMODELS_PATH = '/appmodels'

def create_kubernetes_directory (name):
    k_directory = os.path.join(current_app.config.get('KUBERNETES_FOLDER'), name )  
    if not os.path.isdir(k_directory):
        os.makedirs(k_directory) 
    return k_directory
    
def init_converter (name):   
    if name == 'plexus':
        _id = '60671f549a509804ff59f0a1'
        token_name = 'gitlab+deploy-token-420906'
        token_pass = 'jwCSDnkoZDeZqwf2i9-m'
    if name == 'orbk':
        _id = '60742434a720f657b23c37fc'
        token_name = 'gitlab+deploy-token-420904'
        token_pass = 'gzP9s2bkJV-yeh1a6fn3'        
    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    print(base64_string)
    json_file = {
        "auths": {
            "https://registry.gitlab.com": {
                "auth": base64_string
            }
        }
    }
    json_string = json.dumps(json_file)
    json_base64_string = base64.b64encode(json_string.encode('utf-8')).decode("utf-8")
    create_kubernetes_directory(name)
    namespace(name)
    secret_generation(json_base64_string, name)
    return _id

def appmodels_basepath():
    global APPMODELS_PATH
    return current_app.config.get('UPLOAD_FOLDER') + APPMODELS_PATH

def appmodel_start_app(name):
    """appmodel_start_app

    :param name: 
    :type name: str
    
    :rtype: None
    """
    app_id = init_converter(name)
    try:
        response = requests.get('http://82.214.143.119:31725/application?id=' + app_id )
        response.raise_for_status()
    except HTTPError as http_err:
        error = 'Application ' + name + ' not deployed succesfully due to the following Http error: ' + http_err.msg  
        return {'message': error }, response.status_code
    except:
        error = 'Application ' + name + ' not deployed succesfully due to an unkown error!'
    
    try:
        # access JSOn content
        jsonResponse = response.json()
        print("Entire JSON response")
        print(jsonResponse)
        ReadFile(jsonResponse, name)
    except OSError as err:
        error = 'Application ' + name + ' not deployed succesfully due to the following error: ' + err.strerror
        return {'message': error}, 500
    except:
        error = 'Application ' + name + ' not deployed succesfully due to an unknown error!'
        return {'message': error}, 500
    try:
        config.load_kube_config()
        k8s_client = client.ApiClient()
        kustomization_file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, 'kustomization.yaml')  
        kustomization_file = open(kustomization_file_path, 'rb')
  
        kustomization_file_content = yaml.load(kustomization_file, Loader = yaml.FullLoader)
        kustomization_file.close()
        
        file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, 'namespace.yaml') 
        utils.create_from_yaml(k8s_client, file_path)
        
        if 'secret.yaml' in kustomization_file_content.get('resources'):
            file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, 'secret.yaml') 
            utils.create_from_yaml(k8s_client, file_path)

        for file_name in kustomization_file_content.get('resources'):
            if file_name != 'secret.yaml' and file_name!='namespace.yaml':
                file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, file_name) 
                utils.create_from_yaml(k8s_client, file_path)
    except:
        error = 'Application ' + name + ' not deployed succesfully due to a Kubernetes error!'
        return {'message': error}, 500
    
    return {'message': 'Application with the submitted name has been deployed succesfully!'}, 200

def appmodel_create(body,file):  
    """appmodel_create

    :param app_id: 
    :type app_id: str
    :param file: 
    :type file: str

    :rtype: None
    """

    try:
        file_directory = os.path.join(appmodels_basepath(), body.get('app_id'))
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
