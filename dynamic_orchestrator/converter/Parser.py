import os
from dynamic_orchestrator.converter.Repository import *
from  dynamic_orchestrator.converter.ComputeNode import *
from dynamic_orchestrator.converter.Converter import * 
from dynamic_orchestrator.converter.CloudFramework import *
from dynamic_orchestrator.converter.Container import *

home = str(os.getcwd())


def ReadFile(json):
    nodelist = []
    #resource = ""
    secret = ""

    backend = ""
    requirements = json.get('requirements')
    definitions = requirements[0].get('toscaDescription')
    topology = definitions.get('topology_template')
    node_template = topology.get('node_templates')
    registry = json.get('registry')
    print(registry)
    repolist =[]
    for repository in registry:
        repo = Repository.Repository()
        repo.set_version(repository.get('version'))
        repo.set_imageName(repository.get('imageName'))
        repo.set_path(repository.get('repository'))
        repolist.append(repo)
    node_names = node_template.keys()
    for x in node_names:
        node = node_template.get(x)
        _type = node.get('type')
        properties = node.get('properties')
        if 'Cloud_Framework' in _type:
            cloud = CloudFramework.CloudFramework()
            cloud.set_type(_type)
            if 'actions' in properties:
                actions = properties.get('actions')
                if 'connect' in actions:
                    connect = actions.get('connect')
                    connect_properties = connect.get('properties')
                    backend = connect_properties.get('backend')
                    secret = backend + '-pass'
                    cloud.set_secret_name(backend + '-pass')
                    secret_namespace = connect_properties.get('application')
                    cloud.set_application(secret_namespace)
                    literals = connect_properties.get('literals')
                    cloud.set_literals(literals)
                    order = connect_properties.get('order')
                    cloud.set_order(order)
                if 'connect' not in actions:
                    cloud.set_secret_name(None)
                    cloud.set_literals(None)
                    cloud.set_order(None)
                if 'deploy' in actions:
                    deploy = actions.get('deploy')
                    deploy_properties = deploy.get('properties')
                    application = deploy_properties.get('application')
                    cloud.set_application(application)
                    images = deploy_properties.get('images')
                    cloud.set_images(images)
            nodelist.append(cloud)
        if 'container' in _type:
            container = Container.Container()
            container.set_type(type)
            name = properties.get('name')
            container.set_name(name)
            namespace = properties.get('application')
            container.set_namespace(namespace)
            application = properties.get('application')
            container.set_application(application)
            service = properties.get('service')
            container.set_service(service)
            ingress = properties.get('ingress')
            container.set_ingress(ingress)
            port = properties.get('port')
            container.set_port(port)
            if properties.get('tier'):
                tier = properties.get('tier')
                container.set_tier(tier)
                if tier == 'frontend':
                    container.set_volumeMounts_name(name + '-persistent-storage')
                    container.set_volumeMounts_path('/var/www/html')
                    if 'env' in properties:
                        env_prop = properties.get('env')
                        env_name = env_prop.get('parameters')
                        env = [{'name': env_name.split(',')[0], 'value': backend},
                               {'name': env_name.split(',')[1].lstrip(),
                                'valueFrom': {'secretKeyRef': {'name': secret, 'key': 'password'}}}]
                        container.set_env(env)
                if tier == 'backend':
                    container.set_volumeMounts_name(name + '-persistent-storage')
                    container.set_volumeMounts_path('/var/lib/' + name)
                    if 'env' in properties:
                        env_prop = properties.get('env')
                        env_name = env_prop.get('parameters')
                        env = [{'name': env_name.split(',')[0],
                                'valueFrom': {'secretKeyRef': {'name': secret, 'key': 'password'}}}]
                        container.set_env(env)
            else:
                container.set_tier(None)
            if properties.get('input'):
                _input = properties.get('input')
                input_parameters = _input.get('parameters')
                if "ip" in input_parameters:
                    container_name = container.get_name()
                    if container_name.split('.')[0] == input_parameters.split('.')[0]:
                        env = [
                            {'name': container_name + "_IP", 'valueFrom': {'fieldRef': {'fieldPath': 'status.podIP'}}}]
                        container.set_env(env)
                    else:
                        container.set_env(None)
            else:
                container.set_env(None)
            container.set_volumes_name(name + '-persistent-storage')
            container.set_volumes_claimname(name + '-pv-claim')
            requirements = node.get('requirements')[0]
            host = requirements.get('host')
            node = host.get('node')
            container.set_node(node)
            relationship = host.get('relationship')
            container.set_relatioship(relationship)
            nodelist.append(container)
        if 'EdgeNode' in _type:
            edgenode = ComputeNode.ComputeNode()
            edgenode.set_name(x)
            edgenode.set_type(_type)
            gpu_model = properties.get('gpu_model')
            model = gpu_model.get('model')
            edgenode.set_gpu_model(model)
            dedicated = gpu_model.get('dedicated')
            edgenode.set_gpu_dedicated(dedicated)
            capabilities = node.get('capabilities')
            host = capabilities.get('host')
            host_properties = host.get('properties')
            num_cpus = host_properties.get('num_cpus')
            edgenode.set_num_cpu(num_cpus)
            mem_size = host_properties.get('mem_size')
            edgenode.set_mem_size(mem_size)
            disk_size = host_properties.get('disk_size')
            edgenode.set_disk_size(disk_size)
            os = capabilities.get('os')
            os_properties = os.get('properties')
            os_type = os_properties.get('type')
            edgenode.set_os(os_type)
            nodelist.append(edgenode)
        if 'VM' in _type:
            vm = ComputeNode.ComputeNode()
            vm.set_name(x)
            vm.set_type(_type)
            capabilities = node.get('capabilities')
            host = capabilities.get('host')
            host_properties = host.get('properties')
            num_cpus = host_properties.get('num_cpus')
            vm.set_num_cpu(num_cpus)
            mem_size = host_properties.get('mem_size')
            vm.set_mem_size(mem_size)
            disk_size = host_properties.get('disk_size')
            vm.set_disk_size(disk_size)
            os = capabilities.get('os')
            os_properties = os.get('properties')
            os_type = os_properties.get('type')
            vm.set_os(os_type)
            nodelist.append(vm)
    tosca_to_k8s(nodelist)
