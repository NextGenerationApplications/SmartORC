import random
from decimal import Decimal
import json

def main():
    cluster_file = open('C:\\Users\\Ferrucci\\git\\resource-indexing-discovery\\component\\src\\data\\cluster.json')
    cluster = json.load(cluster_file)
    nodes_file = open('C:\\Users\\Ferrucci\\git\\resource-indexing-discovery\\component\\src\\data\\nodes.json')
    nodes = json.load(nodes_file)
    random.seed()
    for i in range(200):   
        device_name = 'device' + str(i)
        cores = random.randint( 1, 8)
        cpu_arch = random.choice(('x86_64','arm'))
        os_name = random.choice(('Linux','Win'))
        #add the new device in the characterization dictionary
        new_device = {'device':
          {'_id': {'$oid': '60a374f6a501952350daff3b'}, 
            'device_name': device_name, 
            'ip': '192.168.1.203', 
            'type': 'RPi', 
            'UUID': 'da8c5416-b30b-11eb-bc62-204ef6b52cc7', 
            'RAM(bytes)': 4095737856, 
            'Battery': 'None', 
            'CPU': 
                {'model': 'ARMv7 Processor rev 3 (v7l)', 
                'Arch': cpu_arch, 
                'bits': '32', 
                'cores': cores}, 
            'GPU': 
                {'GPU_name': 'Nvidia GeForce RTX 20-series', 
                 'GPU_type': 'dedicated', 
                 'GPU_video_memory(bytes)': 4095737856, 
                 'GPU_total_available_memory(bytes)': 'not available', 
                 'unified_memory': 'yes', 
                 'dedicated_video_memory': 'not available'}, 
            'OS': 
                {'OS_name': 'Linux', 
                'OS_version': '4.19.75-v7l+'}, 
            'DISK': {'size': 45931640320}, 
            'K3s': {'node_role': ''}, 
            'Region': 
                {'continent': 'Europe', 
                 'country': 'Greece', 
                 'city': 'Athens', 
                 'latitude': 37.9842, 
                'longtitude': 23.7353}
            }}
        cluster.append(new_device)
        
        #add the new device in the monitoring dictionary
        
        cpu_percent = '{0:f}'.format(Decimal(random.random()*100))
        cpu_usage = {"node": device_name, 
          "cpu_usage(percentage)": cpu_percent}
          
        ram_available =  str(random.randint( 536870912, 4095737856))
        memory_usage = {"node": device_name, 
          "mem_usage(percentage)": " 46.25", 
          "available_memory(bytes)": ram_available}          
        
        disk_free_space_available =  str(random.randint( 20154875325, 80254715489))

        disk_free_space = {"node": device_name, 
          "disk_free_space(bytes)": disk_free_space_available} 
          
        nodes.get('Results')[0].get('Cpu Usage Results').append(cpu_usage)
        nodes.get('Results')[1].get('Memory Usage Results').append(memory_usage)
        nodes.get('Results')[6].get('Disk Free Space Results').append(disk_free_space)
        
    with open('C:\\Users\\Ferrucci\\git\\resource-indexing-discovery\\component\\src\\data\\cluster-new.json', 'w+', encoding='utf-8') as f:
        json.dump(cluster, f, ensure_ascii=False, indent=4)
        f.close() 
        
    with open('C:\\Users\\Ferrucci\\git\\resource-indexing-discovery\\component\\src\\data\\nodes-new.json', 'w+', encoding='utf-8') as outfile:
        json.dump(nodes, outfile, ensure_ascii=False, indent=4)    
        outfile.close()
        
if __name__ == '__main__':
    main()