#!/usr/bin/env python3

import connexion,sys,getopt,os
from dynamic_orchestrator import encoder
from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator
import ipaddress 

def main(argv):
    try:
        #opts, args = getopt.getopt(argv,"hp:d:k:")
        opts, args = getopt.getopt(argv,"hp:k:b:")
    except getopt.GetoptError:
        #print ('__main__.py -k <kubernetes_app_model_file_folder> -d <upload_file_folder> -p <port_number>')
        print ('__main__.py -f <kubernetes_config_filename> -k <kubernetes_app_model_file_folder> -p <orchestrator_port_number> -b <application_bucket_ip_address_and_port>')
        sys.exit(2)
    upload_folder = '.'
    kubernetes_folder = './kubernetes'
    kubernetes_config_file_name = 'kubeconfig'
    application_bucket_ip_and_port = '82.214.143.119:31725'
    port_number = 8080
    for opt, arg in opts:
        if opt == '-h':
            #print ('__main__.py -k <kubernetes_app_model_file_folder> -d <upload_file_folder> -p <port_number>')
            print ('__main__.py -f  <kubernetes_config_filename> -k <kubernetes_app_model_file_folder> -p <orchestrator_port_number> -b <application_bucket_ip_address_and_port>')
            sys.exit()
        elif opt == "-f":
            kubernetes_config_file_name = arg                 
        elif opt == "-k":
            kubernetes_folder = arg   
        elif opt == "-p":
            try:
                input_port = int(arg)
                if (1 <= input_port  <= 65535):
                    port_number = input_port
                else:                                  
                    sys.exit('-p parameter: Argument is not a valid port number')
            except:
                sys.exit('-p parameter: Argument is not a valid port number')
        elif opt == "-b":
            if isinstance(arg, str):
                try:  
                    application_bucket_ip_and_port = arg.split(':',1)
                    application_bucket_ip = ipaddress.ip_address(application_bucket_ip_and_port[0])
                    application_port_number = application_bucket_ip_and_port[1]
                    if not (1 <= int(application_port_number)  <= 65535):                                                
                        sys.exit('-b parameter: the port number is not valid')
                except ValueError:
                    sys.exit('-b parameter: address/netmask is invalid')
                except:
                    sys.exit('-b parameter: ')
                 
    options = {"swagger_ui": False}
    app = connexion.App(__name__, specification_dir='./dynamic_orchestrator', options = options)
    app.app.json_encoder = encoder.JSONEncoder
    app.app.config['UPLOAD_FOLDER'] = upload_folder
    app.app.config['ORCHESTRATOR'] = ConcreteOrchestrator() 
    app.app.config['KUBERNETES_FOLDER'] = kubernetes_folder 
    app.app.config['KUBERNETES_CONFIG_FILE'] = kubernetes_config_file_name
    app.app.config['APPLICATION_BUCKET_IP'] = application_bucket_ip_and_port
    app.add_api('LM_orchestrator.yaml', arguments={'title': 'OpenApi 3.0 ReST interface for Accordion Orchestrator'}, 
                pythonic_params=True)
    app.run(port=port_number)
if __name__ == '__main__':
    main(sys.argv[1:])

