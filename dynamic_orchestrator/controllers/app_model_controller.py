import connexion
import six

from dynamic_orchestrator.models.inline_response200 import InlineResponse200  # noqa: E501
from dynamic_orchestrator import util
from werkzeug.utils import secure_filename
import os

def appmodel_create(body,file):  # noqa: E501
    """appmodel_create

     # noqa: E501

    :param app_id: 
    :type app_id: str
    :param file: 
    :type file: str

    :rtype: None
    """
    directory = os.path.join('./appmodels/', body.get('app_id'))
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, file.filename)
    if os.path.isfile(filepath):
        return {'status': 'Not Created', 'message': 'A AppModel Yaml file already exists with the given name and identifier'}, 409
    try:
        file.save(filepath)
    except OSError:
        return {'status': 'Not Created', 'message': 'Failed to create AppModel Yaml file with the given name and identifier'}, 500    
    return {'status': 'Created', 'message': 'Record uploaded successfully !'}, 200

def appmodel_delete(app_id):  # noqa: E501
    """appmodel_delete

     # noqa: E501

    :param app_id: 
    :type app_id: str

    :rtype: None
    """
    print('appmodel_delete: ',app_id)
    return 'do some magic!'

def appmodel_read_all():  # noqa: E501
    """appmodel_read_all

    Return the list of the name of Yaml files that contains the representation of the model of the applications submitted until now and the respective identifiers # noqa: E501


    :rtype: List[InlineResponse200]
    """
    return 'do some magic!'


def appmodel_update(app_id,body):  # noqa: E501
    """appmodel_update

     # noqa: E501

    :param body: Substitute the Yaml file that contains the representation of the model of the application with the given identifier with the new file passed as a parameter
    :type body: dict | bytes
    :param app_id: 
    :type app_id: str

    :rtype: None
    """
    
    #ody2 = body.from_dict(connexion.request.get_json())  # noqa: E501
    print('appmodel_update: ',body)
    print('appmodel_update: ',app_id)
    return 'do some magic!'
