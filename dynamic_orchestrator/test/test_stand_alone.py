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
    
#try:
#    file = open('AppModel.yml', 'rb')  
#    m1 = MultipartEncoder(
#    fields={'app_id': 'AppModelFileID1', 
#         'file': ('AppModel.yml', file ,'text/plain')}
#    )  
# 
#    r1 = requests.post("http://localhost:8080/orchestrator/appmodel", data=m1,
#                  headers={'Content-Type': m1.content_type})
#    pretty_print(r1)
#    print(r1.status_code)
#    print(r1.text)
#except Exception as e:
#    print('ConnectionError')
#file.close()

#try:
#    file2 = open('MonitorModel.yml', 'rb')
#    m3 = MultipartEncoder(
#        fields={'federation_id': 'MonitorDataFileID1', 
#         'file': ('MonitorModel.yml', file2,'text/plain')}
#        )
#    r8 = requests.post("http://localhost:8080/orchestrator/monitordata", data=m3,
#                  headers={'Content-Type': m3.content_type})
#    print(r8.status_code)
#    print(r8.text)
#except Exception as e:
#    print('ConnectionError')
#file2.close()

#file3=open('AppModel2.yml', 'rb')
#m2 = MultipartEncoder(
#    fields={'file': ('AppModel2.yml', file3 ,'text/plain')}
#    )  
#r2 = requests.put("http://localhost:8080/orchestrator/appmodel/AppModelFileID1", data=m2,
#                  headers={'Content-Type': m2.content_type})
#pretty_print(r2)
#print(r2.status_code)
#print(r2.text)
#file3.close()

#r3 = requests.get("http://localhost:8080/orchestrator/appmodel")
#pretty_print(r3)
#print(r3.status_code)
#print(r3.text)

#r10 = requests.get("http://localhost:8080/orchestrator/monitordata")
#print(r10.status_code)
#print(r10.text)


#r4 = requests.delete("http://localhost:8080/orchestrator/appmodel/AppModelFileID1")
#pretty_print(r4)
##pretty_print(r4)
#print(r4.status_code)
#print(r4.text)

#r5 = requests.get("http://localhost:8080/orchestrator/appmodel")
#print(r5.status_code)
#print(r5.text) 
#r6 = requests.delete("http://localhost:8080/orchestrator/appmodel/AppModelFileID2")
#print(r6.status_code)
#print(r6.text)

#r7 = requests.get("http://localhost:8080/orchestrator/appmodel")
#print(r7.status_code)
#print(r7.text)
#try:
#    r9 = requests.get("http://localhost:8080/orchestrator/depplan?app_id=AppModelFileID1&federation_id=MonitorDataFileID1")
#    pretty_print(r9)
#    print(r9.status_code)
#    print(r9.text)
#except Exception as e:
#    print('Connection Error')    

try:     
    json_file1 = open('intermidietmodel-UC1.json')
    AB_response = json.load(json_file1)
    #AB_response = requests.get('http://app.accordion-project.eu:31724/application?name=ovr&isLatest=true')
    #AB_resp = requests.get('http://app.accordion-project.eu:31724/application?name=orbk&isLatest=true')
    #AB_response = AB_response.json()
    #print(json.dumps(AB_response))
    #body1 = {'app_component_names':[{'component_name':'accordion-ovr-0-0-3-1654548478-localservice'}], 'operation':'deploy', 'app_model' : AB_response, 'application_parameters': {}}
    body1 = {'app_component_names':[{'component_name':'accordion-ovr-0-0-3-123-localservice'}], 'operation':'deploy', 'app_model' : AB_response, 
             'application_parameters': [{'component_name':'accordion-ovr-0-0-3-123-localservice', 'external_ip':'1.2.3.4','latency_threshold':20,'device_ip':'94.66.223.207'}]}

    #body1 = {'app_component_names':[{'component_name':'accordion-orbk-0-0-1-148-gameserver'}], 'operation':'deploy', 'app_model' : AB_response, 'application_parameters': {}} 
    
    data1 = json.dumps(body1)
    r1 = requests.post('http://localhost:7000/orchestrator/request', data = data1, headers={'Content-type': 'application/json'})
    pretty_print(r1)
    print(r1.status_code)
    print(r1.text)
except Exception as e:
    print('Connection Error with the Orchestrator for the Ovr Use Case')  
    
#try:     
#    json_file2 = open('intermidietmodel-UC1.json')
#    app_model_ovr = json.load(json_file2)
    #r1 = requests.get('http://app.accordion-project.eu:31724/application?name=UC 1&isLatest=true')
#    body2 = {'app_component_names':[{'component_name':'accordion-ovr-0-0-3-1626876643-signalingserver'}], 'operation':'deploy', 'app_model' : app_model_ovr, 'application_parameters': None} 
#    data2 = json.dumps(body2)
#    r2 = requests.post('http://localhost:7000/orchestrator/request', data = data2, headers={'Content-type': 'application/json'})
#    pretty_print(r2)
#    print(r2.status_code)
#    print(r2.text)
#except Exception as e:
#    print('Connection Error with the Orchestrator for the Ovr Use Case')  