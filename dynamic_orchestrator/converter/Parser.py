import os
from dynamic_orchestrator.converter import ComputeNode,Converter,CloudFramework,Container,Repository,Image,MatchingModel
import yaml

home = str(os.getcwd())


def ReadFile(json):
    nodelist = []
    actionlist = []
    resource = ""
    secret = ""
    imagelist = []

    backend = ""
    application = ""
    requirements = json.get('requirements')
    definitions = requirements[0].get('toscaDescription')
    topology = definitions.get('topology_template')
    node_template = topology.get('node_templates')
    registry = json.get('registry')
    application_details = json.get('details')
    application_version = application_details.get('version')
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
                if 'deploy' in actions:
                    component_names = []
                    deploy = actions.get('deploy')
                    deploy_properties = deploy.get('properties')
                    application = deploy_properties.get('application')
                    order = deploy_properties.get("order")
                    images = deploy_properties.get('images')
                    cloud.set_application(application)
                    for image in images:
                        _object = Image.Image()
                        for name, dict_ in image.items():
                            _object.set_internal(dict_.get('internal'))
                            _object.set_path(dict_.get('name'))
                            component_names.append(name.lower())
                            _object.set_name(name)
                            imagelist.append(_object)
                    actionlist.append({'action': 'deploy', 'order': order, 'components': component_names})
                if 'requestSession' in actions:
                    component_names = []
                    createSession = actions.get('requestSession')
                    createSession_properties = createSession.get('properties')
                    application = createSession_properties.get('application')
                    order = createSession_properties.get("order")
                    images = createSession_properties.get('images')
                    cloud.set_application(application)
                    for image in images:
                        _object = Image.Image()
                        for name, dict_ in image.items():
                            _object.set_internal(dict_.get('internal'))
                            _object.set_path(dict_.get('name'))
                            component_names.append(name.lower())
                            _object.set_name(name)
                            imagelist.append(_object)
                    actionlist.append({'action': 'requestSession', 'order': order, 'components': component_names})
                if 'terminate' in actions:
                    component_names = []
                    terminate = actions.get('terminate')
                    terminate_properties = terminate.get('properties')
                    application = terminate_properties.get('application')
                    images = terminate_properties.get('images')
                    order = terminate_properties.get("order")
                    cloud.set_application(application)
                    for image in images:
                        _object = Image.Image()
                        for name, dict_ in image.items():
                            _object.set_internal(dict_.get('internal'))
                            _object.set_path(dict_.get('name'))
                            component_names.append(name.lower())
                            _object.set_name(name)
                            imagelist.append(_object)
                    actionlist.append({'action': 'terminate', 'order': order, 'components': component_names})
                if 'requestAnblick' in actions:
                    component_names = []
                    anblick = actions.get('requestAnblick')
                    anblick_properties = anblick.get('properties')
                    application = anblick_properties.get('application')
                    images = anblick_properties.get('images')
                    order = anblick_properties.get("order")
                    cloud.set_application(application)
                    for image in images:
                        _object = Image.Image()
                        for name, dict_ in image.items():
                            _object.set_internal(dict_.get('internal'))
                            _object.set_path(dict_.get('name'))
                            component_names.append(name)
                            _object.set_name(name)
                            imagelist.append(_object)
                    actionlist.append({'action': 'createSession', 'order': order, 'components': component_names})

                cloud.set_actions(actionlist)
            nodelist.append(cloud)
        if 'Component' in _type:
            container = Container.Container()
            container.set_type(_type)
            name = properties.get('name')
            container.set_name(name)
            container.set_application(application)
            service = properties.get('external_ip')
            container.set_service(service)
            unit = properties.get('deployment_unit')
            if unit == "vm":
                flavor = properties.get("flavor")
                container.set_flavor(flavor)
            container.set_unit(unit)
            port = properties.get('port')
            if port:
                if ', ' in port:
                    ports = port.split(', ')
                    container.set_port(ports)
                else:
                    container.set_port(port)
            else:
                container.set_port(None)
            container.set_volumeMounts_name(name + '-persistent-storage')
            container.set_volumeMounts_path('/var/lib/' + name)
            if properties.get('env'):
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
            container.set_dependency(None)
            if properties.get('dependency'):
                dependency = properties.get('dependency')
                container.set_dependency(dependency)

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
            if properties:
                gpu_model = properties.get('gpu_model')
                if gpu_model:
                    model = gpu_model.get('model')
                    edgenode.set_gpu_model(model)
                    dedicated = gpu_model.get('dedicated')
                    edgenode.set_gpu_dedicated(dedicated)
                wifi_antenna = properties.get('wifi_antenna')
                if wifi_antenna:
                    edgenode.set_wifi_antenna(wifi_antenna)
                if not wifi_antenna:
                    edgenode.set_wifi_antenna("None")
                if not gpu_model:
                    edgenode.set_gpu_model("None")
                    edgenode.set_gpu_dedicated("None")
            if not properties:
                edgenode.set_gpu_model("None")
                edgenode.set_gpu_dedicated("None")
                edgenode.set_wifi_antenna("None")
            capabilities = node.get('capabilities')
            if capabilities.get('host'):
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
            else:
                edgenode.set_num_cpu(None)
                edgenode.set_mem_size(None)
                edgenode.set_disk_size("200 MB")
            os = capabilities.get('os')
            os_properties = os.get('properties')
            os_type = os_properties.get('type')
            architecture = os_properties.get('architecture')
            edgenode.set_architecture(architecture)
            edgenode.set_os(os_type)
            nodelist.append(edgenode)
        if 'PublicCloud' in _type:
            vm = ComputeNode.ComputeNode()
            vm.set_name(x)
            vm.set_type(_type)
            capabilities = node.get('capabilities')
            if capabilities.get('host'):
                host = capabilities.get('host')
                host_properties = host.get('properties')
                num_cpus = host_properties.get('num_cpus')
                vm.set_num_cpu(num_cpus)
                mem_size = host_properties.get('mem_size')
                vm.set_mem_size(mem_size)
                disk_size = host_properties.get('disk_size')
                vm.set_disk_size(disk_size)
            else:
                vm.set_num_cpu(None)
                vm.set_mem_size(None)
                vm.set_disk_size("200 MB")
            os = capabilities.get('os')
            os_properties = os.get('properties')
            os_type = os_properties.get('type')
            vm.set_os(os_type)
            architecture = os_properties.get('architecture')
            vm.set_architecture(architecture)
            nodelist.append(vm)
    return nodelist, imagelist, application_version.replace(".", "-")
