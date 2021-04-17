#!/usr/bin/env python3

import connexion,sys,getopt,os
from dynamic_orchestrator import encoder
from dynamic_orchestrator.core.concrete_orchestrator import ConcreteOrchestrator

def main(argv):
    try:
        #opts, args = getopt.getopt(argv,"hp:d:k:")
        opts, args = getopt.getopt(argv,"hp:k:")
    except getopt.GetoptError:
        #print ('__main__.py -k <kubernetes_app_model_file_folder> -d <upload_file_folder> -p <port_number>')
        print ('__main__.py -k <kubernetes_app_model_file_folder> -p <port_number>')
        sys.exit(2)
    upload_folder = '.'
    kubernetes_folder = './kubernetes'
    kubernetes_config_file_name = 'kubeconfig'
    port_number = 8080
    for opt, arg in opts:
        if opt == '-h':
            #print ('__main__.py -k <kubernetes_app_model_file_folder> -d <upload_file_folder> -p <port_number>')
            print ('__main__.py -k <kubernetes_app_model_file_folder> -p <port_number>')
            sys.exit()
        #elif opt in ("-d"):
        #        if os.path.isdir(arg):
        #            upload_folder = arg   
        #        else:
        #            print('-d parameter: Argument is not a valid directory path')
        #            sys.exit()
        elif opt in ("-f"):
            if isinstance(arg, str):
                kubernetes_config_file_name = arg             
        elif opt in ("-k"):
            if isinstance(arg, str):
                kubernetes_folder = arg   
            else:
                print('-k parameter: Argument is not a valid directory path')
                sys.exit()
        elif opt in ("-p"):
            try:
                input_port = int(arg)
                if (1 <= input_port  <= 65535):
                    port_number = input_port
                else:                                  
                    sys.exit('-p parameter: Argument is not a valid port number')
            except:
                sys.exit('-p parameter: Argument is not a valid port number')
                 
    #if PortNumber.isdigit() and 1 <= int(PortNumber) <= 65535:
    #    print("This is a VALID port number.")
    #else:
    #    print("This is NOT a valid port number.")  
    options = {"swagger_ui": False}
    app = connexion.App(__name__, specification_dir='./dynamic_orchestrator', options = options)
    app.app.json_encoder = encoder.JSONEncoder
    app.app.config['UPLOAD_FOLDER'] = upload_folder
    app.app.config['ORCHESTRATOR'] = ConcreteOrchestrator() 
    app.app.config['KUBERNETES_FOLDER'] = kubernetes_folder 
    app.app.config['KUBERNETES_CONFIG_FILE'] = kubernetes_config_file_name
    app.add_api('dynamic_orchestrator.yaml', arguments={'title': 'OpenApi 3.0 ReST interface for Accordion Orchestrator'}, 
                pythonic_params=True)
    app.run(port=port_number)
if __name__ == '__main__':
    main(sys.argv[1:])

