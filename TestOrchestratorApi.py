import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import yaml
import json


with open('ProvaMonitorModel.yml', 'rb') as f:
	data = yaml.load(f, Loader = yaml.FullLoader)
	print(data)
	m1 = MultipartEncoder(
    fields={'AppID': 'AppModelFileID1', 
            'file': ('ProvaMonitorModel.yml', open('ProvaMonitorModel.yml', 'rb'), 'text/plain')}
    )
	r1 = requests.post("http://localhost:8080/orchestrator/appmodel", data = m1, headers={'Content-Type': m1.content_type})
	print('POST status code: ', r1.status_code)
	print('POST text: ', r1.text)
	#m2 = MultipartEncoder(
    #fields={'FileBody': ('ProvaAppModel.yml', open('ProvaAppModel.yml', 'rb'), 'text/plain')}
    #)
	#r2 = requests.put("http://localhost:8080/orchestrator/appmodel/AppModelFileID1", data = m2, headers={'Content-Type': m2.content_type})
	#print(r2.status_code)
	#print(r2.text)
	
	r3 = requests.get("http://localhost:8080/orchestrator/appmodel")
	print(r3.status_code)
	print(r3.text)
	
	r4 = requests.delete("http://localhost:8080/orchestrator/appmodel/AppModelFileID1")
	print(r4.status_code)
	print(r4.text)
	
	r5 = requests.get("http://localhost:8080/orchestrator/appmodel")
	print(r5.status_code)
	print(r5.text)
	
	#r6 = requests.delete("http://localhost:8080/orchestrator/appmodel/AppModelFileID2")
	#print(r6.status_code)
	#print(r6.text)
	
	#r7 = requests.get("http://localhost:8080/orchestrator/appmodel")
	#print(r7.status_code)
	#print(r7.text)