import os
from dynamic_orchestrator.converter import Action,Workflows,ComputeNode,CloudFramework,Container,Repository,Image
#import yaml

home = str(os.getcwd())


def ReadFile(json):
    nodelist = []

    imagelist = []
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
            application = properties.get('application')
            cloud.set_application(application)
            if 'deployment_phase' in properties:
                actions = properties.get('deployment_phase')
                actionlist = []
                for actionset in actions:
                    component_names = []
                    action = Action.Action()
                    action.set_name(actionset.get('name'))
                    action.set_order(actionset.get('order'))
                    images = actionset.get('components')
                    for image in images:
                        _object = Image.Image()
                        _object.set_image_type(image.get('type'))
                        component_names.append(image.get('component').lower())
                        _object.set_path(image.get('component').lower())
                        _object.set_component(image.get('component'))
                        if not imagelist:
                            imagelist.append(_object)
                        if imagelist[-1].get_path() != image.get('component').lower():
                            imagelist.append(_object)
                    actionlist.append(
                        {'action': action.get_name(), 'order': action.get_order(),
                         'components': images})
                cloud.set_actions(actionlist)
            nodelist.append(cloud)
            if 'workflows' in properties:
                workflows = properties.get('workflows')
                workflowlist = []
                actionlist = []
                for workflowset in workflows:
                    workflow = Workflows.Workflows()
                    workflow.set_scenario(workflowset.get('scenario'))
                    workflow.set_condition(workflowset.get('condition'))
                    actions = workflowset.get('actions')
                    actionlist = []
                    for actionset in actions:
                        component_names = []
                        action = Action.Action()
                        action.set_name(actionset.get('name'))
                        action.set_order(actionset.get('order'))
                        if action.get_name() != 'send':
                            images = actionset.get('components')
                            for image in images:
                                print(image)
                                _object = Image.Image()
                                _object.set_image_type(image.get('type'))
                                component_names.append(image.get('component').lower())
                                _object.set_path(image.get('component').lower())
                                _object.set_component(image.get('component'))

                            actionlist.append(
                                {'action': action.get_name(), 'order': action.get_order(),
                                 'components': images})
                        if action.get_name() == 'send':
                            if actionset.get('input'):
                                target_list = actionset.get('input')
                            for target in target_list:
                                target.update(component=target.get('component').lower(), to=target.get('to').lower())

                            actionlist.append(
                                {'action': action.get_name(), 'order': action.get_order(),
                                 'send': target_list})
                    workflowlist.append({'scenario': workflow.get_scenario(), 'condition': workflow.get_condition(),
                                         'actions': actionlist})
                cloud.set_workflows(workflowlist)
        if 'Component' in _type:
            container = Container.Container()
            container.set_type(_type)
            name = properties.get('name')
            container.set_name(name)
            container.set_application(application)
            service = properties.get('external_ip')
            container.set_service(service)
            unit = properties.get('deployment_unit')
            if unit == "VM":
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
            if properties.get('dependency'):
                dependency = properties.get('dependency')
                container.set_dependency(dependency)
            else:
                container.set_dependency(None)
            container.set_volumes_name(name + '-persistent-storage')
            container.set_volumes_claimname(name + '-pv-claim')
            requirements = node.get('requirements')[0]
            host = requirements.get('host')
            container.set_host(host)
            # here is done the matching between components of the application model and images of the intermediate model
            # VM part is not fully developed since we don't have the description of these images at IM
            for image in imagelist:
                if name == image.get_path():
                    if image.get_image_type() == 'VM':
                        container.set_image(image.get_component().lower())
                    for repo in repolist:
                        print(repo.get_component() + ":" + image.get_component())
                        if repo.get_component() in image.get_component():
                            container.set_image(repo.get_path() + ":" + repo.get_version())
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

    return (nodelist), (imagelist), application_version.replace(".", "-")
