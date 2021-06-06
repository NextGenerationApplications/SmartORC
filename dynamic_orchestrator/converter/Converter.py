import oyaml as yaml
from dynamic_orchestrator.converter import ComputeNode

def tosca_to_k8s(nodelist, imagelist, application):
    images = []
    deployment = {}
    edge_os = ''
    edge_disk = ''
    edge_cpu = ''
    edge_mem = ''
    vm_os = ''
    kustomization_file =[]
    service_files = []
    persistent_files = []
    deployment_files = []
    print(application)
    resource_list = []
    resources = []
    value = 7000
    y = 0
    flag = False
    for x in nodelist:
        if 'Cloud_Framework' in x.get_type():
            resources.append('namespace.yaml')
            for image in imagelist:
                if image.get_internal():
                    flag = True
                deployment_file = image.get_name().lower() + '-deployment' + '.yaml'
                resources.append(deployment_file)
            if flag:
                resources.append('secret.yaml')
            kustomization = {'kustomization': {'resources': resources}}
            kustomization_file.append(kustomization)
        if ('EdgeNode' in x.get_type()) or ('PublicCloud' in x.get_type()):
            resource = ComputeNode.Resource()
            resource.set_os(x.get_os())
            resource.set_cpu(x.get_num_cpu())
            resource.set_mem(x.get_mem_size())
            resource.set_disk(x.get_disk_size())
            resource.set_name(x.get_name())
            resource_list.append(resource)
        if 'Component' in x.get_type():
            if x.get_unit() == 'container':
                host = x.get_node()
                port_yaml = []
                for resource in resource_list:
                    if resource.get_cpu() and resource.get_mem() and resource.get_disk():
                        resource_yaml = {
                            'requests': {'cpu': resource.get_cpu(),
                                         'memory': resource.get_mem(),
                                         'ephemeral-storage': resource.get_disk()}}

                    if host == resource.get_name():
                        filelist = []
                        ports = x.get_port()
                        if isinstance(ports, str):
                            content = {'containerPort': int(ports), 'name': x.get_name()}
                            port_yaml.append(content)
                        if isinstance(ports, list):
                            i = 0
                            for port in ports:
                                i = i + 1
                                content = {'containerPort': int(port), 'name': x.get_name() + str(i)}
                                port_yaml.append(content)
                        if x.get_service():
                            service_port = []
                            for port in port_yaml:
                                value = value + y
                                print(value)
                                content = {'port': value, 'targetPort': int(port.get('containerPort'))}
                                service_port.append(content)
                                y = y + 1
                            service = {'service-' + x.get_name(): {'apiVersion': 'v1',
                                                                   'kind': 'Service',
                                                                   'metadata': {
                                                                       'name': x.get_name(),
                                                                       'namespace': application,
                                                                       'labels': {
                                                                           'app': application}},
                                                                   'spec': {
                                                                       'ports': service_port,
                                                                       'selector': {'app': application},
                                                                       'type': 'LoadBalancer'}}}
                            service_files.append(service)
                        if resource.get_disk():
                            persistent_volume = {'persistent-volume-' + x.get_name(): {'apiVersion': 'v1',
                                                                                       'kind': 'PersistentVolumeClaim',
                                                                                       'metadata': {
                                                                                           'name': x.get_volumes_claimname(),
                                                                                           'namespace': application,
                                                                                           'labels': {
                                                                                               'app': application}},
                                                                                       'spec':
                                                                                           {'accessModes':
                                                                                                ['ReadWriteOnce'],
                                                                                            'resources': {
                                                                                                'requests':
                                                                                                    {
                                                                                                        'storage': resource.get_disk()}}}}}
                            persistent_files.append(persistent_volume)
                        if x.get_internal():
                            if x.get_env() is not None:
                                deployment = {'deployment-' + x.get_name(): {'apiVersion': 'apps/v1',
                                                                             'kind': 'Deployment',
                                                                             'metadata': {'name': x.get_name(),
                                                                                          'namespace': application,
                                                                                          'labels': {
                                                                                              'app': application}},
                                                                             'spec': {
                                                                                 'selector': {
                                                                                     'matchLabels': {
                                                                                         'app': application}},
                                                                                 'strategy': {'type': 'Recreate'},
                                                                                 'template': {
                                                                                     'metadata': {
                                                                                         'labels': {
                                                                                             'app': application}},
                                                                                     'spec': {'containers': [
                                                                                         {'image': x.get_image(),
                                                                                          'name': x.get_name(),
                                                                                          'resources': resource_yaml,
                                                                                          'imagePullPolicy': 'Always',
                                                                                          'env': x.get_env(),
                                                                                          'ports': port_yaml,
                                                                                          'volumeMounts': [{
                                                                                              'name': x.get_volumeMounts_name(),
                                                                                              'mountPath': x.get_volumeMounts_path()}]}],
                                                                                         'volumes': [{
                                                                                             'name': x.get_volumes_name(),
                                                                                             'persistentVolumeClaim': {
                                                                                                 'claimName': x.get_volumes_claimname()}}],
                                                                                         'nodeSelector': {
                                                                                             'beta.kubernetes.io/os': resource.get_os(),
                                                                                             'resource': ''.join(
                                                                                                 [i for i in
                                                                                                  resource.get_name() if
                                                                                                  not i.isdigit()])},
                                                                                         'imagePullSecrets': [
                                                                                             {
                                                                                                 'name': application + '-registry-credentials'}]}}}}}
                                deployment_files.append(deployment)

                            if x.get_env() is None:
                                deployment = {'deployment-' + x.get_name(): {'apiVersion': 'apps/v1',
                                                                             'kind': 'Deployment',
                                                                             'metadata': {'name': x.get_name(),
                                                                                          'namespace': application,
                                                                                          'labels': {
                                                                                              'app': application}},
                                                                             'spec': {
                                                                                 'selector': {
                                                                                     'matchLabels': {
                                                                                         'app': application}},
                                                                                 'strategy': {'type': 'Recreate'},
                                                                                 'template': {
                                                                                     'metadata': {
                                                                                         'labels': {
                                                                                             'app': application}},
                                                                                     'spec': {'containers': [
                                                                                         {'image': x.get_image(),
                                                                                          'name': x.get_name(),
                                                                                          'resources': resource_yaml,
                                                                                          'imagePullPolicy': 'Always',
                                                                                          'ports':
                                                                                              port_yaml,
                                                                                          'volumeMounts': [{
                                                                                              'name': x.get_volumeMounts_name(),
                                                                                              'mountPath': x.get_volumeMounts_path()}]}],
                                                                                         'volumes': [{
                                                                                             'name': x.get_volumes_name(),
                                                                                             'persistentVolumeClaim': {
                                                                                                 'claimName': x.get_volumes_claimname()}}],
                                                                                         'nodeSelector': {
                                                                                             'beta.kubernetes.io/os': resource.get_os(),
                                                                                             'resource': ''.join(
                                                                                                 [i for i in
                                                                                                  resource.get_name() if
                                                                                                  not i.isdigit()])},
                                                                                         'imagePullSecrets': [
                                                                                             {
                                                                                                 'name': application + '-registry-credentials'}]}}}}}
                                deployment_files.append(deployment)
                        if not x.get_internal():
                            if not x.get_env():
                                deployment = {'deployment-' + x.get_name(): {'apiVersion': 'apps/v1',
                                                                             'kind': 'Deployment',
                                                                             'metadata': {'name': x.get_name(),
                                                                                          'namespace': application,
                                                                                          'labels': {
                                                                                              'app': application}},
                                                                             'spec': {
                                                                                 'selector': {
                                                                                     'matchLabels': {
                                                                                         'app': application, }},
                                                                                 'strategy': {'type': 'Recreate'},
                                                                                 'template': {
                                                                                     'metadata': {
                                                                                         'labels': {
                                                                                             'app': application, }},
                                                                                     'spec': {'containers': [
                                                                                         {'image': x.get_image(),
                                                                                          'name': x.get_name(),
                                                                                          'resources': resource_yaml,
                                                                                          'imagePullPolicy': 'Always',
                                                                                          'ports':
                                                                                              port_yaml,
                                                                                          'volumeMounts': [{
                                                                                              'name': x.get_volumeMounts_name(),
                                                                                              'mountPath': x.get_volumeMounts_path()}]}],
                                                                                         'volumes': [{
                                                                                             'name': x.get_volumes_name(),
                                                                                             'persistentVolumeClaim': {
                                                                                                 'claimName': x.get_volumes_claimname()}}],
                                                                                         'nodeSelector': {
                                                                                             'beta.kubernetes.io/os': resource.get_os(),
                                                                                             'resource': ''.join(
                                                                                                 [i for i in
                                                                                                  resource.get_name() if
                                                                                                  not i.isdigit()])}}}}}}
                                deployment_files.append(deployment)
                            else:
                                deployment = {'deployment-' + x.get_name(): {'apiVersion': 'apps/v1',
                                                                             'kind': 'Deployment',
                                                                             'metadata': {'name': x.get_name(),
                                                                                          'namespace': application,
                                                                                          'labels': {
                                                                                              'app': application}},
                                                                             'spec': {
                                                                                 'selector': {
                                                                                     'matchLabels': {
                                                                                         'app': application, }},
                                                                                 'strategy': {'type': 'Recreate'},
                                                                                 'template': {
                                                                                     'metadata': {
                                                                                         'labels': {
                                                                                             'app': application, }},
                                                                                     'spec': {'containers': [
                                                                                         {'image': x.get_image(),
                                                                                          'name': x.get_name(),
                                                                                          'resources': resource_yaml,
                                                                                          'imagePullPolicy': 'Always',
                                                                                          'env': x.get_env(),
                                                                                          'ports':
                                                                                              port_yaml,
                                                                                          'volumeMounts': [{
                                                                                              'name': x.get_volumeMounts_name(),
                                                                                              'mountPath': x.get_volumeMounts_path()}]}],
                                                                                         'volumes': [{
                                                                                             'name': x.get_volumes_name(),
                                                                                             'persistentVolumeClaim': {
                                                                                                 'claimName': x.get_volumes_claimname()}}],
                                                                                         'nodeSelector': {
                                                                                             'beta.kubernetes.io/os': resource.get_os(),
                                                                                             'resource': ''.join(
                                                                                                 [i for i in
                                                                                                  resource.get_name() if
                                                                                                  not i.isdigit()])}}}}}}
                                deployment_files.append(deployment)
            else:
                host = x.get_node()
                for resource in resource_list:
                    if resource.get_cpu() and resource.get_mem() and resource.get_disk():
                        resource_yaml = {
                            'requests': {'cpu': resource.get_cpu(),
                                         'memory': resource.get_mem(),
                                         'ephemeral-storage': resource.get_disk()}}

                    if host == resource.get_name():
                        if resource.get_disk():
                            persistent_volume = {'persistent-volume-' + x.get_name(): {'apiVersion': 'v1',
                                                                                       'kind': 'PersistentVolumeClaim',
                                                                                       'metadata': {
                                                                                           'name': x.get_volumes_claimname(),
                                                                                           'namespace': application,
                                                                                           'labels': {
                                                                                               'app': application},
                                                                                           'annotations':
                                                                                               {
                                                                                                   'cdi.kubevirt.io/storage.import.endpoint': x.get_image()}},
                                                                                       'spec':
                                                                                           {'accessModes':
                                                                                                ['ReadWriteOnce'],
                                                                                            'resources': {
                                                                                                'requests':
                                                                                                    {
                                                                                                        'storage': resource.get_disk()}}}}}
                            persistent_files.append(persistent_volume)
                        if x.get_service():
                            if x.get_service():
                                service_port = []
                                ports = x.get_port()
                                i = 0
                                for port in ports:
                                    i = i + 1
                                    content = {'name': 'remote-desktop-' + str(i), 'port': int(port),
                                               'targetPort': 3389}
                                    port_yaml.append(content)
                                    service_port.append(content)
                                service = {'service-' + x.get_name(): {'apiVersion': 'v1',
                                                                       'kind': 'Service',
                                                                       'metadata': {
                                                                           'name': x.get_name(),
                                                                           'namespace': application,
                                                                           'labels': {
                                                                               'app': application}},
                                                                       'spec': {
                                                                           'externalTrafficPolicy': 'Cluster',
                                                                           'ports': service_port,
                                                                           'selector': {'app': application},
                                                                           'type': 'LoadBalancer'}}}
                                service_files.append(service)
                        if not x.get_internal():
                            deployment = {'deployment-' + x.get_name(): {'apiVersion': 'kubevirt.io/v1',
                                                                         'kind': 'VirtualMachine',
                                                                         'metadata': {'name': x.get_name(),
                                                                                      'namespace': application,
                                                                                      'generation': 1,
                                                                                      'labels': {
                                                                                          'kubevirt.io/os': 'linux'}},
                                                                         'spec': {
                                                                             'running': True,
                                                                             'template': {
                                                                                 'metadata': {
                                                                                     'labels': {
                                                                                         'kubevirt.io/domain': x.get_flavor()}},
                                                                                 'spec': {'domain': {'cpu': {
                                                                                     'cores': int(resource.get_cpu())},
                                                                                     'devices': {
                                                                                         'disks': [{
                                                                                             'disk': {
                                                                                                 'bus': 'virtio'},
                                                                                             'name': 'disk0'},
                                                                                             {
                                                                                                 'cdrom': {
                                                                                                     'bus': 'sata',
                                                                                                     'readonly': True},
                                                                                                 'name': 'cloudinitdisk'}]},
                                                                                     'machine': {
                                                                                         'type': 'q35'},
                                                                                     'resources': {
                                                                                         'requests': {
                                                                                             'memory': resource.get_mem()}}},
                                                                                     'volumes': [
                                                                                         {'name': 'disk0',
                                                                                          'persistentVolumeClaim': {
                                                                                              'claimName': x.get_volumes_claimname()}},
                                                                                         {
                                                                                             'cloudInitNoCloud': {
                                                                                                 'userData': {
                                                                                                     'hostname': x.get_name(),
                                                                                                     'ssh_pwauth': True,
                                                                                                     'disable_root': False,
                                                                                                     'ssh_authorized_key': [
                                                                                                         'ssh-rsa YOUR_SSH_PUB_KEY_HERE']},
                                                                                             },
                                                                                             'name': 'cloudinitdisk'}]}}}}}
                            deployment_files.append(deployment)
    return deployment_files, persistent_files, service_files, kustomization_file


def secret_generation(json, application):
    secret = {'secret-' + application: {'apiVersion': 'v1',
                                        'kind': 'Secret',
                                        'metadata': {
                                            'name': application + '-registry-credentials',
                                            'namespace': application},
                                        'type': 'kubernetes.io/dockerconfigjson',
                                        'data': {
                                            '.dockerconfigjson': json}}}
    return secret


def namespace(application):
    namespace = {
        'namespace-' + application: {'apiVersion': 'v1', 'kind': 'Namespace', 'metadata': {'name': application}}}

    return namespace
