import os
import json


def generate(nodelist, application,path_name):
    json_template = {}
    resourcelist = []

    for x in nodelist:
        if x.get_type() == 'tosca.nodes.Compute.EdgeNode':
            edge_node_name = x.get_name()
            print(edge_node_name)
            edge_cpu = x.get_num_cpu()
            edge_disk = x.get_disk_size()
            edge_mem = x.get_mem_size()
            edge_gpu_type = x.get_gpu_dedicated()
            edge_gpu = x.get_gpu_model()
            edge_os = x.get_os()
            if edge_gpu is not None:
                json_requirements = {'type': edge_node_name, 'os': edge_os,
                                     'hardware_requirements': {'cpu': edge_cpu, 'ram': edge_mem, 'disk': edge_disk,
                                                               'gpu': {'model': edge_gpu, 'dedicated': edge_gpu_type}}}
            else:
                json_requirements = {'type': edge_node_name, 'os': edge_os,
                                     'hardware_requirements': {'cpu': edge_cpu, 'ram': edge_mem, 'disk': edge_disk}
                                     }
            resourcelist.append(json_requirements)

        if 'PublicCloud' in x.get_type():
            vm_node_name = x.get_name()
            vm_cpu = x.get_num_cpu()
            vm_disk = x.get_disk_size()
            vm_mem = x.get_mem_size()
            vm_os = x.get_os()
            json_requirements = {'type': vm_node_name, 'os': vm_os,
                                 'hardware_requirements': {'cpu': vm_cpu, 'ram': vm_mem, 'disk': vm_disk}
                                 }
            resourcelist.append(json_requirements)
    json_template[application] = []
    nodelist = [i for i in nodelist if i.get_type() != "tosca.nodes.Compute.EdgeNode"]
    nodelist = [i for i in nodelist if i.get_type() != "tosca.nodes.Compute.PublicCloud"]
    nodelist = [i for i in nodelist if i.get_type() != "ACCORDION.Cloud_Framework"]
    if not os.path.exists(application + '_output'):
        os.makedirs(application + '_output')
    print(len(nodelist))
    print(len(resourcelist))
    print(resourcelist)
    for x in nodelist:
        for y in resourcelist:
            if x.get_node() == y.get('type'):
                y.pop('type')
                unit = x.get_unit()
                name = x.get_name()
                if x.get_port():
                    port = x.get_port()
                else:
                    port = "None"
                host = x.get_node()
                result = ''.join([i for i in host if not i.isdigit()])
                dependency = x.get_dependency()
                if not dependency:
                    json_template[application].append({
                        'component': name,
                        'unit': unit,
                        'port': port,
                        'host': {
                            'host_type': result,
                            'requirements': y
                        }
                    })
                if dependency:
                    json_template[application].append({
                        'component': name,
                        'unit': unit,
                        'port': port,
                        'dependency': dependency,
                        'host': {
                            'host_type': result,
                            'requirements': y
                        }
                    })

    with open(path_name + '_output' + '/' + path_name + '_internal_model.json', 'w') as outfile:
        json.dump(json_template, outfile)
