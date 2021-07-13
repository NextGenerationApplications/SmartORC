#!/usr/bin/env python3

import connexion,sys,getopt
from dynamic_orchestrator import encoder
import logging
#from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator

VERSION = 1.0 

def main(argv):
    try:
        #opts, args = getopt.getopt(argv,"hp:d:k:")
        opts, args = getopt.getopt(argv,"hp:")
    except getopt.GetoptError:
        #print ('__main__.py -k <kubernetes_app_model_file_folder> -d <upload_file_folder> -p <port_number>')
        print ('__main__.py -p <orchestrator_port_number>')
        sys.exit(2)
    #kubernetes_folder = './kubernetes'
    #kubernetes_config_file_name = 'kubeconfig'
    port_number = 7000
    for opt, arg in opts:
        if opt == '-h':
            #print ('__main__.py -k <kubernetes_app_model_file_folder> -d <upload_file_folder> -p <port_number>')
            #print ('__main__.py -f  <kubernetes_config_filename> -k <kubernetes_app_model_file_folder> -p <orchestrator_port_number>')
            print ('__main__.py -p <orchestrator_port_number>')
            sys.exit()
        elif opt == "-p":
            try:
                input_port = int(arg)
                if (1 <= input_port  <= 65535):
                    port_number = input_port
                else:                                  
                    sys.exit('-p parameter: Argument is not a valid port number')
            except:
                sys.exit('-p parameter: Argument is not a valid port number')
    ##------------------ Configure logging
    # create logger
    logger = logging.getLogger('ACCORDION Orchestrator')
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to warning
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter('[%(asctime)s,%(msecs)d] %(name)s/%(threadName)s/%(funcName)s (line: %(lineno)d) %(levelname)s: %(message)s', '%d/%b/%Y %H:%M:%S')
    # add formatter to console handler (ch)
    ch.setFormatter(formatter)
    # add console handler (ch) to logger
    logger.addHandler(ch)
    # logger can be used as logger.debug(str) or logger.info(str) or logger.warning(str) or logger.error(str) or logger.critical(str)
    
    # Initialize logging level constants (to be used in method /setLoggingLevel)
    loggingLevels = {}
    loggingLevels["CRITICAL"] = logging.CRITICAL
    loggingLevels["ERROR"] = logging.ERROR
    loggingLevels["WARNING"] = logging.WARNING
    loggingLevels["INFO"] = logging.INFO
    loggingLevels["DEBUG"] = logging.DEBUG
    
    logger.info("ACCORDION Orchestrator version %s" % VERSION)                
    options = {"swagger_ui": False}
    app = connexion.App(__name__, specification_dir='./dynamic_orchestrator', options = options)
    app.app.json_encoder = encoder.JSONEncoder
    #app.app.config['ORCHESTRATOR'] = ConcreteOrchestrator() 
    #app.app.config['KUBERNETES_FOLDER'] = kubernetes_folder 
    #app.app.config['KUBERNETES_CONFIG_FILE'] = kubernetes_config_file_name
    app.add_api('Orchestrator_LM.yaml', arguments={'title': 'OpenApi 3.0 ReST interface for Accordion Orchestrator'}, 
                pythonic_params=True)
    app.run(port=port_number)
    
    
    
if __name__ == '__main__':
    main(sys.argv[1:])

