# System modules
from datetime import datetime
import yaml
import connexion
import os
from flask import make_response, abort
from werkzeug.utils import secure_filename
import shutil

ListAppModels = dict()
first_time = True

APPMODELS_PATH = './appmodels'

def fill_ListAppModels():
	global ListAppModels, first_time, APPMODELS_PATH
	if first_time:
		first_time = False
		if os.path.isdir(APPMODELS_PATH):
			AppModelsDirList = os.listdir(APPMODELS_PATH)
			for name in AppModelsDirList:
				directory =  os.path.join(APPMODELS_PATH,name)
				if os.path.isdir(directory):
					AppModelsFileDirList = os.listdir(directory)
					for filename in AppModelsFileDirList:
						ListAppModels[name] = filename

def read_all():
	global ListAppModels
	fill_ListAppModels()
	result = []
	for k, v in ListAppModels.items():
		result.append({'filename': v,'AppID': k})

	return result

def create(FileBody):
	global APPMODELS_PATH, ListAppModels
	record = connexion.request.files['file']
	filename = secure_filename(record.filename)
	directory = os.path.join(APPMODELS_PATH, FileBody.get('AppID'))
	os.makedirs(directory, exist_ok=True)
	filepath = os.path.join(directory, record.filename)
	if os.path.isfile(filepath):
		return {'status': 'Not Created', 'message': 'A AppModel Yaml file already exists with the given name and given identifier'}, 409
	try:
		record.save(filepath)
	except OSError as e:
		return {'status': 'Not Created', 'message': 'Failed to create AppModel Yaml file with the given name and identifier'}, 500	
	ListAppModels[FileBody.get('AppID')] = filename
	return {'status': 'Created', 'message': 'Record uploaded successfully !'}, 201

def update(AppID, FileBody):
	global APPMODELS_PATH, ListAppModels
	record = connexion.request.files[FileBody]
	print(record)
	return


def delete(AppID):
	global APPMODELS_PATH, ListAppModels
	fill_ListAppModels()
	if AppID in ListAppModels:
		filename = ListAppModels[AppID]
		directory = os.path.join(APPMODELS_PATH, AppID)
		if os.path.isdir(directory):
			try:
				shutil.rmtree(directory)
			except OSError as e:
				return {'status': 'Not Deleted', 'message': 'Failed to delete AppModel Yaml file with the given identifier'}, 500	
			ListAppModels.pop(AppID)
	else:
		return{'status': 'Not Deleted', 'message': 'A AppModel Yaml file not exists with that name and given identifier'},409
	return {'status': 'Deleted', 'message':'AppModel Yaml file with the given identifier deleted succesfully'}, 201