# System modules
from datetime import datetime

# 3rd party modules
from flask import make_response, abort


def read_all():

    return [PEOPLE[key] for key in sorted(PEOPLE.keys())]

def create():
	return null
	
def update():
	return null

def delete():
	return null