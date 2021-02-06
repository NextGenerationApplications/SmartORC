import connexion
import six

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server import util


def appmodel_create(app_id, file):  # noqa: E501
    """appmodel_create

     # noqa: E501

    :param app_id: 
    :type app_id: str
    :param file: 
    :type file: strstr

    :rtype: None
    """
    return 'do some magic!'


def appmodel_read_all():  # noqa: E501
    """appmodel_read_all

    Return the list of the name of Yaml files that contains the representation of the model of the applications submitted until now and the respective identifiers # noqa: E501


    :rtype: List[InlineResponse200]
    """
    return 'do some magic!'


def appmodel_update(body, app_id):  # noqa: E501
    """appmodel_update

     # noqa: E501

    :param body: Substitute the Yaml file that contains the representation of the model of the application with the given identifier with the new file passed as a parameter
    :type body: dict | bytes
    :param app_id: 
    :type app_id: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
