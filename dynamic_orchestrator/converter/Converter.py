import oyaml as yaml
from dynamic_orchestrator.converter.ComputeNode import *


def tosca_to_k8s(nodelist):
    images = []
    deployment = {}
    edge_os = ''
    edge_disk = ''
    edge_cpu = ''
    edge_mem = ''
    vm_os = ''
    vm_cpu = ''
    vm_disk = ''
    vm_mem = ''
    resource_list = []
    resources = []
    application = ""
    for x in nodelist:
        if 'Cloud_Framework' in x.get_type():
            images = x.get_images()
            application = x.get_application()
            namespace = {'apiVersion': 'v1', 'kind': 'Namespace', 'metadata': {'name': application}}
            with open('kubernetes/' + application + '/namespace.yaml', 'w') as outfile:
                yaml.dump(namespace, outfile, default_flow_style=False)
            resources.append('namespace.yaml')
            for image in images:
                for name, dict_ in image.items():
                    deployment_file = name.lower() + '-deployment' + '.yaml'
                    resources.append(deployment_file)
            kustomization = {'resources': resources}
            if x.get_secret_name() is not None:
                secret_name = x.get_secret_name()
                literals = x.get_literals()
                resources.append('namespace.yaml')
                kustomization = {
                    'secretGenerator': [{'name': secret_name, 'namespace': namespace, 'literals': literals}],
                    'resources': resources}
                with open('kubernetes/' + application + '/kustomization.yaml', 'w') as outfile:
                    yaml.dump(kustomization, outfile, default_flow_style=False)
            with open('kubernetes/' + application + '/kustomization.yaml', 'w') as outfile:
                yaml.dump(kustomization, outfile, default_flow_style=False)
        if ('EdgeNode' in x.get_type()) or ('VM' in x.get_type()):
            resource = ComputeNode.Resource()
            resource.set_os(x.get_os())
            resource.set_cpu(x.get_num_cpu())
            resource.set_mem(x.get_mem_size())
            resource.set_disk(x.get_disk_size())
            resource.set_name(x.get_name())
            resource_list.append(resource)
        if 'container' in x.get_type():
            host = x.get_node()
            for resource in resource_list:
                if host == resource.get_name():
                    filelist = []
                    for i in images:
                        for name, dict_ in i.items():
                            if x.get_name() in name.lower():
                                image = dict_.get('name') + ':latest'
                    if x.get_service():
                        service = {'apiVersion': 'v1',
                                   'kind': 'Service',
                                   'metadata': {
                                       'name': x.get_name(),
                                       'namespace': x.get_namespace(),
                                       'labels': {
                                           'app': x.get_application()}},
                                   'spec': {
                                       'ports': [{'port': x.get_port()}],
                                       'selector': {'app': x.get_application(), 'tier': x.get_tier()},
                                       'clusterIP': 'None'}}
                        filelist.append(service)
                    persistent_volume = {'apiVersion': 'v1',
                                         'kind': 'PersistentVolumeClaim',
                                         'metadata': {
                                             'name': x.get_volumes_claimname(),
                                             'namespace': x.get_namespace(),
                                             'labels': {
                                                 'app': x.get_application()}},
                                         'spec':
                                             {'accessModes':
                                                  ['ReadWriteOnce'],
                                              'resources': {
                                                  'requests':
                                                      {'storage': resource.get_disk()}}}}
                    filelist.append(persistent_volume)
                    if x.get_ingress():
                        ingress = {'apiVersion': 'extensions/v1beta1',
                                   'kind': 'Ingress',
                                   'metadata': {'name': x.get_name(), 'namespace': x.get_namespace()},
                                   'spec': {
                                       'rules': [{'host': x.get_name() + '.nip.io',
                                                  'http': {'paths': [
                                                      {'backend': {'serviceName': x.get_name(), 'servicePort': 'web'},
                                                       'path': '/'}]}}],
                                       'tls': [{'hosts': [x.get_name() + '.nip.io']}]}}
                        filelist.append(ingress)
                    if host and (x.get_tier() is not None) and x.get_env() is not None:
                        deployment = {'apiVersion': 'apps/v1',
                                      'kind': 'Deployment',
                                      'metadata': {'name': x.get_name(), 'namespace': x.get_application(),
                                                   'labels': {'app': x.get_application()}},
                                      'spec': {
                                          'selector': {
                                              'matchLabels': {'app': x.get_application(), 'tier': x.get_tier()}},
                                          'strategy': {'type': 'Recreate'},
                                          'template': {
                                              'metadata': {
                                                  'labels': {'app': x.get_application(), 'tier': x.get_tier()}},
                                              'spec': {'hostNetwork': True, 'containers': [
                                                  {'image': image, 'name': x.get_name(),
                                                   'resources': {
                                                       'requests': {'cpu': resource.get_cpu(),
                                                                    'memory': resource.get_mem(),
                                                                    'ephemeral-storage': resource.get_disk()}},
                                                   'imagePullPolicy': 'Always',
                                                   'env': x.get_env(),
                                                   'ports': [
                                                       {'containerPort': x.get_port(), 'name': x.get_name()}],
                                                   'volumeMounts': [{'name': x.get_volumeMounts_name(),
                                                                     'mountPath': x.get_volumeMounts_path()}]}],
                                                       'volumes': [{'name': x.get_volumes_name(),
                                                                    'persistentVolumeClaim': {
                                                                        'claimName': x.get_volumes_claimname()}}],
                                                       'nodeSelector': {'beta.kubernetes.io/os': resource.get_os(),
                                                                        'resource': resource.get_name()}}}}}
                        filelist.append(deployment)
                        with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                  'w') as outfile:
                            yaml.dump_all(
                                filelist,
                                outfile,
                                default_flow_style=False
                            )
                    if host and x.get_tier() is None:
                        deployment = {'apiVersion': 'apps/v1',
                                      'kind': 'Deployment',
                                      'metadata': {'name': x.get_name(), 'namespace': x.get_application(),
                                                   'labels': {'app': x.get_application()}},
                                      'spec': {
                                          'selector': {
                                              'matchLabels': {'app': x.get_application(), }},
                                          'strategy': {'type': 'Recreate'},
                                          'template': {
                                              'metadata': {
                                                  'labels': {'app': x.get_application(), }},
                                              'spec': {'containers': [
                                                  {'image': image, 'name': x.get_name(),
                                                   'resources': {
                                                       'requests': {'cpu': resource.get_cpu(),
                                                                    'memory': resource.get_mem(),
                                                                    'ephemeral-storage': resource.get_disk()}},
                                                   'imagePullPolicy': 'Always',
                                                   'ports': [
                                                       {'containerPort': x.get_port(), 'name': x.get_name()}]}],
                                                  'nodeSelector': {'beta.kubernetes.io/os': resource.get_os(),
                                                                   'resource': resource.get_name()}}}}}
                        filelist.append(deployment)
                        with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                  'w') as outfile:
                            yaml.dump_all(
                                filelist,
                                outfile,
                                default_flow_style=False
                            )

                    if host and x.get_env() is not None:
                        deployment = {'apiVersion': 'apps/v1',
                                      'kind': 'Deployment',
                                      'metadata': {'name': x.get_name(), 'namespace': x.get_application(),
                                                   'labels': {'app': x.get_application()}},
                                      'spec': {
                                          'selector': {
                                              'matchLabels': {'app': x.get_application(), 'tier': x.get_tier()}},
                                          'strategy': {'type': 'Recreate'},
                                          'template': {
                                              'metadata': {
                                                  'labels': {'app': x.get_application(), 'tier': x.get_tier()}},
                                              'spec': {'hostNetwork': True, 'containers': [
                                                  {'image': image, 'name': x.get_name(),
                                                   'resources': {
                                                       'requests': {'cpu': resource.get_cpu(),
                                                                    'memory': resource.get_mem(),
                                                                    'ephemeral-storage': resource.get_disk()}},
                                                   'imagePullPolicy': 'Always',
                                                   'env': x.get_env(),
                                                   'ports': [
                                                       {'containerPort': x.get_port(), 'name': x.get_name()}],
                                                   }],

                                                       'nodeSelector': {'beta.kubernetes.io/os': resource.get_os(),
                                                                        'resource': resource.get_name()}}}}}
                        filelist.append(deployment)
                        with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                  'w') as outfile:
                            yaml.dump_all(
                                filelist,
                                outfile,
                                default_flow_style=False
                            )
                    if host and (x.get_tier() is not None) and x.get_env() is None:
                        deployment = {'apiVersion': 'apps/v1',
                                      'kind': 'Deployment',
                                      'metadata': {'name': x.get_name(), 'namespace': x.get_application(),
                                                   'labels': {'app': x.get_application()}},
                                      'spec': {
                                          'selector': {
                                              'matchLabels': {'app': x.get_application(), 'tier': x.get_tier()}},
                                          'strategy': {'type': 'Recreate'},
                                          'template': {
                                              'metadata': {
                                                  'labels': {'app': x.get_application(), 'tier': x.get_tier()}},
                                              'spec': {'hostNetwork': True, 'containers': [
                                                  {'image': image, 'name': x.get_name(),
                                                   'resources': {
                                                       'requests': {'cpu': resource.get_cpu(),
                                                                    'memory': resource.get_mem(),
                                                                    'ephemeral-storage': resource.get_disk()}},
                                                   'imagePullPolicy': 'Always',
                                                   'ports': [
                                                       {'containerPort': x.get_port(), 'name': x.get_name()}],
                                                   'volumeMounts': [{'name': x.get_volumeMounts_name(),
                                                                     'mountPath': x.get_volumeMounts_path()}]}],
                                                       'volumes': [{'name': x.get_volumes_name(),
                                                                    'persistentVolumeClaim': {
                                                                        'claimName': x.get_volumes_claimname()}}],
                                                       'nodeSelector': {'beta.kubernetes.io/os': resource.get_os(),
                                                                        'resource': resource.get_name()}}}}}
                        filelist.append(deployment)
                        with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                  'w') as outfile:
                            yaml.dump_all(
                                filelist,
                                outfile,
                                default_flow_style=False
                            )
