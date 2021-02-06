import connexion
import six

from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server import util


def monitordata_create(app_id, file):  # noqa: E501
    """monitordata_create

     # noqa: E501

    :param app_id: 
    :type app_id: str
    :param file: 
    :type file: strstr

    :rtype: None
    """
    return 'do some magic!'


def monitordata_read_all():  # noqa: E501
    """monitordata_read_all

    Return the list of the name of Yaml files that contains the availability of resources of an entire federation and the respective identifiers # noqa: E501


    :rtype: List[InlineResponse2001]
    """
    return 'do some magic!'


def monitordata_update(body, federation_id):  # noqa: E501
    """monitordata_update

     # noqa: E501

    :param body: Substitute a Yaml file that contains the representation of the availability of resources of an entire federation with the given identifier with the new file passed as a parameter
    :type body: dict | bytes
    :param federation_id: 
    :type federation_id: str

    :rtype: None
    """
    if connexion.request.is_json:
        body = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
