import logging

import connexion
from flask_testing.utils import TestCase
from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator
from dynamic_orchestrator.encoder import JSONEncoder


class BaseTestCase(TestCase):

    def create_app(self):
        options = {"swagger_ui": False}
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='./',options = options)
        app.app.json_encoder = JSONEncoder
        app.app.config['UPLOAD_FOLDER'] = './'
        app.app.config['ORCHESTRATOR'] = ConcreteOrchestrator() 
        app.add_api('../dynamic_orchestrator.yaml',arguments={'title': 'OpenApi 3.0 ReST interface for Accordion Orchestrator'}, pythonic_params=True)
        return app.app
