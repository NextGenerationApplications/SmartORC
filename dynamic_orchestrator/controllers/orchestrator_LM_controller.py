import connexion
import six
from dynamic_orchestrator.converter.Parser import ReadFile
from dynamic_orchestrator.converter.MatchingModel import generate
from dynamic_orchestrator.converter.Converter import namespace,secret_generation, tosca_to_k8s  
from dynamic_orchestrator.models.inline_response500 import InlineResponse500  # noqa: E501
from dynamic_orchestrator.models.request_body import RequestBody  # noqa: E501
from dynamic_orchestrator import util
from  urllib.error import HTTPError
from kubernetes import client, config, utils
import base64
import json
import yaml
from werkzeug.utils import secure_filename
import os
import shutil
from flask import current_app
import requests

# APPMODELS_PATH = '/appmodels'

def choose_application (app_instance_id):   
    name = app_instance_id.split('-')[1]
    if name == 'plexus':
        token_name = 'gitlab+deploy-token-420906'
        token_pass = 'jwCSDnkoZDeZqwf2i9-m'
    if name == 'orbk':
        token_name = 'gitlab+deploy-token-420904'
        token_pass = 'gzP9s2bkJV-yeh1a6fn3'
    if name == 'ovr':
        token_name = 'gitlab+deploy-token-430087'
        token_pass = 'NDxnnzt9WvuR7zyAHchX'
    return token_name, token_pass

def secret (app_instance_id):  
    token_name, token_pass = choose_application(app_instance_id)
    sample_string = token_name + ":" + token_pass
    sample_string_bytes = sample_string.encode("ascii")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    json_file = {
        "auths": {
            "https://registry.gitlab.com": {
                "auth": base64_string
            }
        }
    }
    json_string = json.dumps(json_file)
    json_base64_string = base64.b64encode(json_string.encode('utf-8')).decode("utf-8")
    return json_base64_string

def create_kubernetes_directory (name):
    k_directory = os.path.join(current_app.config.get('KUBERNETES_FOLDER'), name )  
    if not os.path.isdir(k_directory):
        os.makedirs(k_directory) 
    return k_directory

#def appmodels_basepath():
#    global APPMODELS_PATH
#    return current_app.config.get('UPLOAD_FOLDER') + APPMODELS_PATH

def orchestrator_LM_request(body):  # noqa: E501
    """orchestrator_lm_request

    Receive a request from the Lifecycle Manager ACCORDION component # noqa: E501

    :param body: The parameters of the request received from the LM
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = RequestBody.from_dict(connexion.request.get_json())  # noqa: E501
        name = body.app_instance_id.split('-')[1]
    try:        
        _namespace = "accordion-" + name
        namespace_yaml = namespace(_namespace)
        secret_yaml = secret_generation(secret (body.app_instance_id), _namespace)
        nodelist, imagelist = ReadFile(body.app_model, _namespace, name)
        deployment_files, persistent_files, service_files, kustomization_file = tosca_to_k8s(nodelist, imagelist, _namespace)
        print(namespace_yaml)
        print(secret_yaml)
        print(deployment_files)
        matchmaking_model = generate(nodelist, _namespace, name)
        print(matchmaking_model)
    except OSError as err:
        error = 'Application ' + name + ' not deployed successfully due to the following error: ' + err.strerror
        return {'message': error}, 500
    except:
        error = 'Application ' + name + ' not deployed successfully due to an unknown error!'
        return {'message': error}, 500
    try:     
        kube_config_file = os.path.join( './config', current_app.config.get('KUBERNETES_CONFIG_FILE'))
        config.load_kube_config(kube_config_file)
        k8s_client = client.ApiClient()
        kustomization_file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, 'kustomization.yaml')  
        kustomization_file = open(kustomization_file_path, 'rb')
  
        kustomization_file_content = yaml.safe_load(kustomization_file)
        kustomization_file.close()
        
        file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, '_namespace.yaml') 
        result = utils.create_from_yaml(k8s_client, file_path, verbose=True, pretty=True)
        if 'secret.yaml' in kustomization_file_content.get('resources'):
            file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, 'secret.yaml') 
            result = utils.create_from_yaml(k8s_client, file_path, verbose=True, pretty=True)

        for file_name in kustomization_file_content.get('resources'):
            if file_name != 'secret.yaml' and file_name!='_namespace.yaml':
                file_path = os.path.join(current_app.config.get('KUBERNETES_FOLDER') , name, file_name) 
                result = utils.create_from_yaml(k8s_client, file_path, verbose=True, pretty=True)

    except utils.FailToCreateError as KubeErr:
        error = 'Application ' + name + ' not deployed succesfully due to a Kubernetes error! '
        print(KubeErr)
        return {'message': error}, 500
    
    return {'message': 'Application with the submitted name has been deployed succesfully!'}, 200