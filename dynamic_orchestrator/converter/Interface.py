import random
import string
import Image
import requests
from requests.exceptions import HTTPError
from Kafka_Producer import Producer
import ActionModel
import MatchingModel
import Parser
import base64
import json
import Converter
import WorkflowModel


def generateID():
    S = 10  # number of characters in the string.
    # call random.choices() string module to find the string in Uppercase + numeric data.
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k=S))
    return str(ran.lower())


def callAppBucket(json_base64_string, url, name):
    try:
        response = requests.get(url)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        print("Entire JSON response")
        print(jsonResponse)
        # Generate a random ID to emulate the running instance ID
        ID = generateID()
        # Parse Intermediate Model
        nodelist, imagelist, application_version = Parser.ReadFile(jsonResponse)
        # Create the namespace that describes the running instance component
        namespace = "accordion-" + name + "-" + application_version + "-" + ID
        # Generate configuration files for Orchestrator
        namespace_yaml = Converter.namespace(namespace)
        secret_yaml = Converter.secret_generation(json_base64_string, namespace)

        # model for orchestrator that has the requirements of components
        matchmaking_model = MatchingModel.generate(nodelist, namespace)
        print(matchmaking_model)
        # minicloud that is decided through matchmaking process
        minicloud = "minicloud5"
        externalIP = "'1.2.4.114'"
        deployment_files, persistent_files, service_files = Converter.tosca_to_k8s(nodelist, imagelist,
                                                                                   namespace, minicloud, externalIP)

        # model for lifecycle manager that has actions, their order and related components
        actions_set = ActionModel.generate(nodelist, namespace)
        print(actions_set)
        workflows_set = WorkflowModel.generate(nodelist)
        print(workflows_set)
        print(namespace_yaml)
        print(secret_yaml)
        print(deployment_files)
        print(matchmaking_model)
        print(persistent_files)
        print(service_files)
        Image.image_model(imagelist)
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')


def online_selector(name):
    if name == 'plexus':
        url = 'http://app.accordion-project.eu:31724/application?name=plexus&isLatest=true'
        token_name = 'gitlab+deploy-token-420906'
        token_pass = 'jwCSDnkoZDeZqwf2i9-m'
        jsonResponse = open('intermidietmodel-UC3.json')
        data = json.loads(jsonResponse.read())
        print(data)
    if name == 'orbk':
        url = 'http://app.accordion-project.eu:31724/application?name=orbk&isLatest=true'
        token_name = 'gitlab+deploy-token-420904'
        token_pass = 'gzP9s2bkJV-yeh1a6fn3'
        jsonResponse = open('intermidietmodel-UC2.json')
        # data = json.loads(jsonResponse.read())
        # print(data)
    if name == 'ovr':
        url = 'http://app.accordion-project.eu:31724/application?name=ovr&isLatest=true'
        token_name = 'gitlab+deploy-token-430087'
        token_pass = 'NDxnnzt9WvuR7zyAHchX'
        jsonResponse = open('intermidietmodel-UC1.json')
        # data = json.loads(jsonResponse.read())
        # print(data)
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
    json_base64 = base64.b64encode(json_string.encode('utf-8'))
    json_base64_string = json_base64.decode("utf-8")

    callAppBucket(json_base64_string, url, name, jsonResponse)


def offline_selector(name):
    if name == 'plexus':
        jsonResponse = open('intermidietmodel-UC3.json')
        data = json.loads(jsonResponse.read())
        token_name = 'gitlab+deploy-token-420906'
        token_pass = 'jwCSDnkoZDeZqwf2i9-m'
        print(data)
    if name == 'orbk':
        jsonResponse = open('intermidietmodel-UC2.json')
        data = json.loads(jsonResponse.read())
        token_name = 'gitlab+deploy-token-420904'
        token_pass = 'gzP9s2bkJV-yeh1a6fn3'
        print(data)
    if name == 'ovr':
        jsonResponse = open('intermidietmodel-UC1.json')
        data = json.loads(jsonResponse.read())
        token_name = 'gitlab+deploy-token-430087'
        token_pass = 'NDxnnzt9WvuR7zyAHchX'
        print(data)
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
    json_base64 = base64.b64encode(json_string.encode('utf-8'))
    json_base64_string = json_base64.decode("utf-8")

    # Parse Intermediate Model
    nodelist, imagelist, application_version = Parser.ReadFile(data)
    # Application type
    application_type = "accordion-" + name + "-" + application_version
    # Generate a random ID to emulate the running instance ID
    ID = generateID()
    # Create the namespace that describes the running instance component
    application_instance = application_type + "-" + ID

    # minicloud that is decided through matchmaking process
    minicloud = "minicloud5"
    externalIP = "'1.2.4.114'"
    # model for orchestrator that has the requirements of components
    matchmaking_model = MatchingModel.generate(nodelist, application_type)
    # Generate configuration files for Orchestrator
    namespace_yaml = Converter.namespace(application_instance)
    secret_yaml = Converter.secret_generation(json_base64_string, application_instance)
    deployment_files, persistent_files, service_files = Converter.tosca_to_k8s(nodelist, imagelist,
                                                                               application_instance, minicloud,
                                                                               externalIP)

    # model for lifecycle manager that has actions, their order and related components
    actions_set = ActionModel.generate(nodelist, application_type)

    print(actions_set)
    # workflows for lifecycle manager
    workflows_set = WorkflowModel.generate(nodelist, application_type)
    print(workflows_set)
    print(namespace_yaml)
    print(secret_yaml)
    print(deployment_files)
    print(matchmaking_model)
    # dict to json string
    json_string = json.dumps(matchmaking_model)
    producer = Producer()
    # send json string to broker
    producer.send_message('accordion.monitoring.reservedResources', json_string)
    print(persistent_files)
    print(service_files)


offline_selector('orbk')
