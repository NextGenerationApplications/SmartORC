import requests
#from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

def pretty_print(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.request.method + ' ' + req.request.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.request.headers.items()),
        req.request.body,
    ))

try:     
    #json_file1 = open('intermidietmodel-UC2.json')
    #app_model_orbk = json.load(json_file1)
    AB_resp = requests.get('http://192.168.0.115:8000/get-file/ac-ovr-ls-part.tar.xz')
    pass
    #AB_resp = requests.get('http://app.accordion-project.eu:31724/application?name=orbk&isLatest=true')
    #AB_response = AB_resp.json()
    
    #body1 = {'app_component_names':[{'component_name':'accordion-ovr-0-0-3-1487523654-localservice'}], 'operation':'deploy', 'app_model' : AB_response, 'application_parameters': {}}
    #body1 = {'app_component_names':[{'component_name':'accordion-orbk-0-0-1-1487523654-gameserver'}], 'operation':'deploy', 'app_model' : AB_response, 'application_parameters': {}} 
 
    #data1 = json.dumps(body1)
    #r1 = requests.post('http://localhost:7000/orchestrator/request', data = data1, headers={'Content-type': 'application/json'})
    pretty_print(AB_resp)
    #print(r1.status_code)
    #print(r1.text)
except Exception as e:
    print('Connection Error with the fetchVMimage server')  