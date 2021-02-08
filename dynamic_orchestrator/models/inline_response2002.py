from __future__ import absolute_import
from dynamic_orchestrator.models.base_model_ import Model
from dynamic_orchestrator import util


class InlineResponse2002(Model):

    def __init__(self, file: str=None): 
        """InlineResponse2002 - a model defined in Swagger

        :param file: The file of this InlineResponse2002. 
        :type file: str
        """
        self.swagger_types = {
            'file': str
        }

        self.attribute_map = {
            'file': 'file'
        }
        self._file = file

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse2002':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_2 of this InlineResponse2002. 
        :rtype: InlineResponse2002
        """
        return util.deserialize_model(dikt, cls)

    @property
    def file(self) -> str:
        """Gets the file of this InlineResponse2002.


        :return: The file of this InlineResponse2002.
        :rtype: str
        """
        return self._file

    @file.setter
    def file(self, file: str):
        """Sets the file of this InlineResponse2002.


        :param file: The file of this InlineResponse2002.
        :type file: str
        """

        self._file = file
