import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

file = open('AppModel.yml', 'rb')	
m1 = MultipartEncoder(
   fields={'app_id': 'AppModelFileID1', 
         'file': ('AppModel.yml', file ,'text/plain')}
   )
	
r1 = requests.post("http://localhost:8080/orchestrator/appmodel", data=m1,
                  headers={'Content-Type': m1.content_type})
	
print(r1.status_code)
print(r1.text)
file.close()

file2 = open('MonitorModel.yml', 'rb')
m3 = MultipartEncoder(
   fields={'federation_id': 'MonitorDataFileID1', 
         'file': ('MonitorModel.yml', file2,'text/plain')}
   )
r8 = requests.post("http://localhost:8080/orchestrator/monitordata", data=m3,
                  headers={'Content-Type': m3.content_type})
print(r8.status_code)
print(r8.text)
file2.close()

#file3=open('MonitorModel.yml', 'rb')
#m2 = {'body': ('MonitorModel.yml', file3,'text/plain')}
#r2 = requests.put("http://localhost:8080/orchestrator/appmodel/AppModelFileID1", files = m2)
#print(r2.status_code)
#print(r2.text)
#file3.close()

r3 = requests.get("http://localhost:8080/orchestrator/appmodel")
print(r3.status_code)
print(r3.text)

r10 = requests.get("http://localhost:8080/orchestrator/monitordata")
print(r10.status_code)
print(r10.text)


#r4 = requests.delete("http://localhost:8080/orchestrator/appmodel/AppModelFileID1")
#print(r4.status_code)
#print(r4.text)

r5 = requests.get("http://localhost:8080/orchestrator/appmodel")
print(r5.status_code)
print(r5.text)
	
r6 = requests.delete("http://localhost:8080/orchestrator/appmodel/AppModelFileID2")
print(r6.status_code)
print(r6.text)

r7 = requests.get("http://localhost:8080/orchestrator/appmodel")
print(r7.status_code)
print(r7.text)

r9 = requests.get("http://localhost:8080/orchestrator/depplan?app_id=AppModelFileID1&federation_id=MonitorDataFileID1")
print(r9.status_code)
print(r9.text)