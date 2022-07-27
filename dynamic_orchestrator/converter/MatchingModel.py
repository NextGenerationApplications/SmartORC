import os
import json


def convert_bytes(bytes):
    output = 0
    if 'Mi' in bytes:
        number = bytes.replace('Mi', ' ')
        output = int(number) * 1024 * 1024
    if 'Gi' in bytes:
        number = bytes.replace('Gi', ' ')
        output = int(number) * 1024 * 1024 * 1024
    return output


def manage_dependencies(dependencies, application):
    for d in dependencies:
        name = d.get('component')
        new_name = application + "-" + name.lower()
        d.update((k, new_name) for k, v in d.items() if v == name)


def generate(nodelist, application):
    json_template = {}
    resourcelist = []

    for x in nodelist:
        if x.get_type() == 'tosca.nodes.Compute.EdgeNode':
            edge_node_name = x.get_name()
            edge_cpu = x.get_num_cpu()
            edge_disk = str(convert_bytes(x.get_disk_size()))
            edge_mem = str(convert_bytes(x.get_mem_size()))
            edge_gpu_type = x.get_gpu_dedicated()
            edge_gpu = x.get_gpu_model()
            edge_os = x.get_os()
            edge_architecture = x.get_architecture()
            if edge_gpu is not None:
                json_requirements = {'type': edge_node_name, 'os': edge_os, 'arch': edge_architecture,
                                     'hardware_requirements': {'cpu': str(edge_cpu), 'ram': edge_mem, 'disk': edge_disk,
                                                               'gpu': {'model': edge_gpu,
                                                                       'dedicated': str(edge_gpu_type)}}}
                resourcelist.append(json_requirements)
            else:
                json_requirements = {'type': edge_node_name, 'os': edge_os, 'arch': edge_architecture,
                                     'hardware_requirements': {'cpu': str(edge_cpu), 'ram': edge_mem, 'disk': edge_disk}
                                     }
                resourcelist.append(json_requirements)

        if x.get_type() == 'tosca.nodes.Compute.PublicCloud':
            vm_node_name = x.get_name()
            vm_cpu = x.get_num_cpu()
            vm_disk = str(convert_bytes(x.get_disk_size()))
            vm_mem = str(convert_bytes(x.get_mem_size()))
            vm_os = x.get_os()
            vm_arch = x.get_architecture()
            json_requirements = {'type': vm_node_name, 'os': vm_os, 'arch': vm_arch,
                                 'hardware_requirements': {'cpu': str(vm_cpu), 'ram': vm_mem, 'disk': vm_disk}
                                 }
            resourcelist.append(json_requirements)
    json_template[application] = []
    nodelist = [i for i in nodelist if i.get_type() != "tosca.nodes.Compute.EdgeNode"]
    nodelist = [i for i in nodelist if i.get_type() != "tosca.nodes.Compute.PublicCloud"]
    nodelist = [i for i in nodelist if i.get_type() != "ACCORDION.Cloud_Framework"]

    for x in nodelist:
        for y in resourcelist:
            if x.get_host() == y.get('type'):
                print(y)
                print(x.get_name())
                unit = x.get_unit()
                name = x.get_name()
                if x.get_port():
                    port = x.get_port()
                    if type(port) != list:
                        port_list = []
                        port_list.append(port)
                        host = x.get_host()
                        result = ''.join([i for i in host if not i.isdigit()])

                        dependecy = x.get_dependency()
                        if not dependecy:
                            json_template[application].append({
                                'component': application + "-" + name,
                                'unit': unit,
                                'port': port_list,
                                'host': {
                                    'host_type': result,
                                    'requirements': y
                                }
                            })
                        if dependecy:
                            manage_dependencies(dependecy, application)
                            json_template[application].append({
                                'component': application + "-" + name,
                                'unit': unit,
                                'port': port_list,
                                'dependency': dependecy,
                                'host': {
                                    'host_type': result,
                                    'requirements': y
                                }
                            })
                    else:
                        host = x.get_host()
                        result = ''.join([i for i in host if not i.isdigit()])
                        dependecy = x.get_dependency()
                        if not dependecy:
                            json_template[application].append({
                                'component': application + "-" + name,
                                'unit': unit,
                                'port': port,
                                'host': {
                                    'host_type': result,
                                    'requirements': y
                                }
                            })
                        if dependecy:
                            manage_dependencies(dependecy, application)
                            json_template[application].append({
                                'component': application + "-" + name,
                                'unit': unit,
                                'port': port,
                                'dependency': dependecy,
                                'host': {
                                    'host_type': result,
                                    'requirements': y
                                }
                            })
                else:
                    host = x.get_host()
                    result = ''.join([i for i in host if not i.isdigit()])
                    dependecy = x.get_dependency()
                    if not dependecy:
                        json_template[application].append({
                            'component': application + "-" + name,
                            'unit': unit,
                            'host': {
                                'host_type': result,
                                'requirements': y
                            }
                        })
                    if dependecy:
                        manage_dependencies(dependecy, application)
                        json_template[application].append({
                            'component': application + "-" + name,
                            'unit': unit,
                            'dependency': dependecy,
                            'host': {
                                'host_type': result,
                                'requirements': y
                            }
                        })
    return json_template
