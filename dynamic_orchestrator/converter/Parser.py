import os
from dynamic_orchestrator.converter import ComputeNode,Converter,CloudFramework,Container,Repository,Image
import yaml

home = str(os.getcwd())


def ReadFile(json, namespace):
    nodelist = []
    resource = ""
    secret = ""
    imagelist = []
    backend = ""
    requirements = json.get('requirements')
    definitions = requirements[0].get('toscaDescription')
    topology = definitions.get('topology_template')
    node_template = topology.get('node_templates')
    registry = json.get('registry')
    print(registry)
    repolist = []
    for repository in registry:
        repo = Repository.Repository()
        repo.set_version(repository.get('version'))
        repo.set_imageName(repository.get('imageName'))
        repo.set_path(repository.get('repository'))
        repo.set_component(repository.get('component'))
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
                    for image in images:
                        _object = Image.Image()
                        for name, dict_ in image.items():
                            _object.set_internal(dict_.get('internal'))
                            _object.set_path(dict_.get('name'))
                            _object.set_name(name)
                            imagelist.append(_object)
            nodelist.append(cloud)
        if 'container' in _type:
            container = Container.Container()
            container.set_type(_type)
            name = properties.get('name')
            container.set_name(name)
            application = properties.get('application')
            container.set_application(application)
            service = properties.get('service')
            container.set_service(service)
            ingress = properties.get('ingress')
            container.set_ingress(ingress)
            port = properties.get('port')
            if ', ' in port:
                ports = port.split(', ')
                container.set_port(ports)
            else:
                container.set_port(port)
            if properties.get('tier'):
                tier = properties.get('tier')
                container.set_tier(tier)
                container.set_volumeMounts_name(name + '-persistent-storage')
                if tier == 'frontend':
                    container.set_volumeMounts_path('/var/www/html')
                if tier == 'backend':
                    container.set_volumeMounts_path('/var/lib/' + name)
            else:
                container.set_tier(None)
            if properties.get('env'):
                print(properties.get('env'))
                container.set_env(properties.get('env'))
            else:
                container.set_env(None)
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
            container.set_volumes_name(name + '-persistent-storage')
            container.set_volumes_claimname(name + '-pv-claim')
            requirements = node.get('requirements')[0]
            host = requirements.get('host')
            node = host.get('node')
            container.set_node(node)
            relationship = host.get('relationship')
            container.set_relatioship(relationship)
            for image in imagelist:
                if name == image.get_name().lower():
                    if not image.get_internal():
                        container.set_internal(image.get_internal())
                        container.set_image(image.get_path())
                    if image.get_internal():
                        for repo in repolist:
                            if repo.get_component() in image.get_name():
                                container.set_image(repo.get_path() + ":" + repo.get_version())
                                container.set_internal(image.get_internal())
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
            if host_properties.get('disk_size') is not None:
                disk_size = host_properties.get('disk_size')
                edgenode.set_disk_size(disk_size)
            else:
                edgenode.set_disk_size("200 MB")
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
    Converter.tosca_to_k8s(nodelist, imagelist, namespace)
