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
    vm_cpu = ''
    vm_disk = ''
    vm_mem = ''
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
            kustomization = {'resources': resources}
            if x.get_secret_name() is not None:
                secret_name = x.get_secret_name()
                literals = x.get_literals()
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
        if 'component' in x.get_type():
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
                            service = {'apiVersion': 'v1',
                                       'kind': 'Service',
                                       'metadata': {
                                           'name': x.get_name(),
                                           'namespace': application,
                                           'labels': {
                                               'app': application}},
                                       'spec': {
                                           'ports': service_port,
                                           'selector': {'app': application, 'tier': x.get_tier()},
                                           'type': 'LoadBalancer'}}
                            filelist.append(service)
                        if resource.get_disk():
                            persistent_volume = {'apiVersion': 'v1',
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
                                                              {'storage': resource.get_disk()}}}}
                            filelist.append(persistent_volume)
                        if x.get_internal():
                            if (x.get_tier() is not None) and x.get_env() is not None:
                                deployment = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'metadata': {'name': x.get_name(), 'namespace': application,
                                                           'labels': {'app': application}},
                                              'spec': {
                                                  'selector': {
                                                      'matchLabels': {'app': application, 'tier': x.get_tier()}},
                                                  'strategy': {'type': 'Recreate'},
                                                  'template': {
                                                      'metadata': {
                                                          'labels': {'app': application, 'tier': x.get_tier()}},
                                                      'spec': {'containers': [
                                                          {'image': x.get_image(), 'name': x.get_name(),
                                                           'resources': resource_yaml,
                                                           'imagePullPolicy': 'Always',
                                                           'env': x.get_env(),
                                                           'ports': port_yaml,
                                                           'volumeMounts': [{'name': x.get_volumeMounts_name(),
                                                                             'mountPath': x.get_volumeMounts_path()}]}],
                                                          'volumes': [{'name': x.get_volumes_name(),
                                                                       'persistentVolumeClaim': {
                                                                           'claimName': x.get_volumes_claimname()}}],
                                                          'nodeSelector': {
                                                              'beta.kubernetes.io/os': resource.get_os(),
                                                              'resource': ''.join([i for i in resource.get_name() if
                                                                                   not i.isdigit()])},
                                                          'imagePullSecrets': [
                                                              {'name': application + '-registry-credentials'}]}}}}
                                filelist.append(deployment)
                                with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                          'w') as outfile:
                                    yaml.dump_all(
                                        filelist,
                                        outfile,
                                        default_flow_style=False
                                    )
                            if x.get_tier() is None:
                                deployment = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'metadata': {'name': x.get_name(), 'namespace': application,
                                                           'labels': {'app': application}},
                                              'spec': {
                                                  'selector': {
                                                      'matchLabels': {'app': application, }},
                                                  'strategy': {'type': 'Recreate'},
                                                  'template': {
                                                      'metadata': {
                                                          'labels': {'app': application, }},
                                                      'spec': {'containers': [
                                                          {'image': x.get_image(), 'name': x.get_name(),
                                                           'resources': resource_yaml,
                                                           'imagePullPolicy': 'Always',
                                                           'ports':
                                                               port_yaml}],
                                                          'nodeSelector': {'beta.kubernetes.io/os': resource.get_os(),
                                                                           'resource': ''.join(
                                                                               [i for i in resource.get_name() if
                                                                                not i.isdigit()])},
                                                          'imagePullSecrets': [
                                                              {'name': application + '-registry-credentials'}]}}}}
                                filelist.append(deployment)
                                with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                          'w') as outfile:
                                    yaml.dump_all(
                                        filelist,
                                        outfile,
                                        default_flow_style=False
                                    )

                            if x.get_env() is not None:
                                deployment = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'metadata': {'name': x.get_name(), 'namespace': application,
                                                           'labels': {'app': application}},
                                              'spec': {
                                                  'selector': {
                                                      'matchLabels': {'app': application, 'tier': x.get_tier()}},
                                                  'strategy': {'type': 'Recreate'},
                                                  'template': {
                                                      'metadata': {
                                                          'labels': {'app': application, 'tier': x.get_tier()}},
                                                      'spec': {'containers': [
                                                          {'image': x.get_image(), 'name': x.get_name(),
                                                           'resources': resource_yaml,
                                                           'imagePullPolicy': 'Always',
                                                           'env': x.get_env(),
                                                           'ports':
                                                               port_yaml,
                                                           }],

                                                          'nodeSelector': {
                                                              'beta.kubernetes.io/os': resource.get_os(),
                                                              'resource': ''.join([i for i in resource.get_name() if
                                                                                   not i.isdigit()])},
                                                          'imagePullSecrets': [
                                                              {'name': application + '-registry-credentials'}]}}}}
                                filelist.append(deployment)
                                with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                          'w') as outfile:
                                    yaml.dump_all(
                                        filelist,
                                        outfile,
                                        default_flow_style=False
                                    )
                            if (x.get_tier() is not None) and x.get_env() is None:
                                deployment = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'metadata': {'name': x.get_name(), 'namespace': application,
                                                           'labels': {'app': application}},
                                              'spec': {
                                                  'selector': {
                                                      'matchLabels': {'app': application, 'tier': x.get_tier()}},
                                                  'strategy': {'type': 'Recreate'},
                                                  'template': {
                                                      'metadata': {
                                                          'labels': {'app': application, 'tier': x.get_tier()}},
                                                      'spec': {'containers': [
                                                          {'image': x.get_image(), 'name': x.get_name(),
                                                           'resources': resource_yaml,
                                                           'imagePullPolicy': 'Always',
                                                           'ports':
                                                               port_yaml,
                                                           'volumeMounts': [{'name': x.get_volumeMounts_name(),
                                                                             'mountPath': x.get_volumeMounts_path()}]}],
                                                          'volumes': [{'name': x.get_volumes_name(),
                                                                       'persistentVolumeClaim': {
                                                                           'claimName': x.get_volumes_claimname()}}],
                                                          'nodeSelector': {
                                                              'beta.kubernetes.io/os': resource.get_os(),
                                                              'resource': ''.join([i for i in resource.get_name() if
                                                                                   not i.isdigit()])},
                                                          'imagePullSecrets': [
                                                              {'name': application + '-registry-credentials'}]}}}}
                                filelist.append(deployment)
                                with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                          'w') as outfile:
                                    yaml.dump_all(
                                        filelist,
                                        outfile,
                                        default_flow_style=False
                                    )
                        if not x.get_internal():
                            if not x.get_env():
                                deployment = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'metadata': {'name': x.get_name(), 'namespace': application,
                                                           'labels': {'app': application}},
                                              'spec': {
                                                  'selector': {
                                                      'matchLabels': {'app': application, 'tier': x.get_tier()}},
                                                  'strategy': {'type': 'Recreate'},
                                                  'template': {
                                                      'metadata': {
                                                          'labels': {'app': application, 'tier': x.get_tier()}},
                                                      'spec': {'containers': [
                                                          {'image': x.get_image(), 'name': x.get_name(),
                                                           'resources': resource_yaml,
                                                           'imagePullPolicy': 'Always',
                                                           'ports':
                                                               port_yaml,
                                                           'volumeMounts': [{'name': x.get_volumeMounts_name(),
                                                                             'mountPath': x.get_volumeMounts_path()}]}],
                                                          'volumes': [{'name': x.get_volumes_name(),
                                                                       'persistentVolumeClaim': {
                                                                           'claimName': x.get_volumes_claimname()}}],
                                                          'nodeSelector': {
                                                              'beta.kubernetes.io/os': resource.get_os(),
                                                              'resource': ''.join(
                                                                  [i for i in resource.get_name() if
                                                                   not i.isdigit()])}}}}}
                                filelist.append(deployment)
                                with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                          'w') as outfile:
                                    yaml.dump_all(
                                        filelist,
                                        outfile,
                                        default_flow_style=False
                                    )
                            else:
                                deployment = {'apiVersion': 'apps/v1',
                                              'kind': 'Deployment',
                                              'metadata': {'name': x.get_name(), 'namespace': application,
                                                           'labels': {'app': application}},
                                              'spec': {
                                                  'selector': {
                                                      'matchLabels': {'app': application, 'tier': x.get_tier()}},
                                                  'strategy': {'type': 'Recreate'},
                                                  'template': {
                                                      'metadata': {
                                                          'labels': {'app': application, 'tier': x.get_tier()}},
                                                      'spec': {'containers': [
                                                          {'image': x.get_image(), 'name': x.get_name(),
                                                           'resources': resource_yaml,
                                                           'imagePullPolicy': 'Always',
                                                           'env': x.get_env(),
                                                           'ports':
                                                               port_yaml,
                                                           'volumeMounts': [{'name': x.get_volumeMounts_name(),
                                                                             'mountPath': x.get_volumeMounts_path()}]}],
                                                          'volumes': [{'name': x.get_volumes_name(),
                                                                       'persistentVolumeClaim': {
                                                                           'claimName': x.get_volumes_claimname()}}],
                                                          'nodeSelector': {
                                                              'beta.kubernetes.io/os': resource.get_os(),
                                                              'resource': ''.join(
                                                                  [i for i in resource.get_name() if
                                                                   not i.isdigit()])}}}}}
                                filelist.append(deployment)
                                with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                          'w') as outfile:
                                    yaml.dump_all(
                                        filelist,
                                        outfile,
                                        default_flow_style=False
                                    )
            else:
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
                        if resource.get_disk():
                            persistent_volume = {'apiVersion': 'v1',
                                                 'kind': 'PersistentVolumeClaim',
                                                 'metadata': {
                                                     'name': x.get_volumes_claimname(),
                                                     'namespace': application,
                                                     'labels': {
                                                         'app': application},
                                                     'annotations':
                                                         {'cdi.kubevirt.io/storage.import.endpoint': x.get_image()}},
                                                 'spec':
                                                     {'accessModes':
                                                          ['ReadWriteOnce'],
                                                      'resources': {
                                                          'requests':
                                                              {'storage': resource.get_disk()}}}}
                            filelist.append(persistent_volume)
                        if not x.get_internal():
                            deployment = {'apiVersion': 'kubevirt.io/v1',
                                          'kind': 'VirtualMachine',
                                          'metadata': {'name': x.get_name(), 'namespace': application,
                                                       'generation': 1,
                                                       'labels': {'kubevirt.io/os': 'linux'}},
                                          'spec': {
                                              'running': True,
                                              'template': {
                                                  'metadata': {
                                                               'labels': {'kubevirt.io/domain': x.get_flavor()}},
                                                  'spec': {'domain': {'cpu': {'cores': int(resource.get_cpu())},
                                                                      'devices': {
                                                                          'disks': [{'disk': {'bus': 'virtio'},
                                                                                     'name': 'disk0'},
                                                                                    {'cdrom': {'bus': 'sata',
                                                                                               'readonly': True},
                                                                                     'name': 'cloudinitdisk'}]},
                                                                      'machine': {'type': 'q35'}, 'resources': {
                                                          'requests': {'memory': resource.get_mem()}}},
                                                           'volumes': [
                                                               {'name': 'disk0', 'persistentVolumeClaim': {
                                                                   'claimName': x.get_volumes_claimname()}}, {
                                                                   'cloudInitNoCloud': {
                                                                       'userData': {'hostname': x.get_name(),
                                                                                    'ssh_pwauth': True,
                                                                                    'disable_root': False,
                                                                                    'ssh_authorized_key': [
                                                                                        'ssh-rsa YOUR_SSH_PUB_KEY_HERE']},
                                                                   }, 'name': 'cloudinitdisk'}]}}}}

                            filelist.append(deployment)
                            with open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml',
                                      'w') as outfile:
                                yaml.dump_all(
                                    filelist,
                                    outfile,
                                    default_flow_style=False
                                )
                            a_file = open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml', "r")
                            list_of_lines = a_file.readlines()
                            line=0
                            location = 0
                            while line < len(list_of_lines):
                                if "userData:" in list_of_lines[line]:
                                    location = line
                                    print(line)
                                line = line + 1
                            list_of_lines[location] = "         userData: | \n"

                            a_file = open('kubernetes/' + application + '/' + x.get_name() + '-deployment' + '.yaml', "w")
                            a_file.writelines(list_of_lines)
                            a_file.close()


def secret_generation(json, application):
    kubernetes = {'apiVersion': 'v1',
                  'kind': 'Secret',
                  'metadata': {
                      'name': application + '-registry-credentials',
                      'namespace': application},
                  'type': 'kubernetes.io/dockerconfigjson',
                  'data': {
                      '.dockerconfigjson': json}}

    with open('kubernetes/' + application + '/secret.yaml', 'w') as outfile:
        yaml.dump(kubernetes, outfile, default_flow_style=False)


def namespace(application):
    namespace = {'apiVersion': 'v1', 'kind': 'Namespace', 'metadata': {'name': application}}
    with open('kubernetes/' + application + '/namespace.yaml', 'w') as outfile:
        yaml.dump(namespace, outfile, default_flow_style=False)
