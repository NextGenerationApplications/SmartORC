from hurry.filesize import size, iec


def convert_bytes(bytes):
    output = 0
    if 'MB' in bytes:
        number = bytes.replace('MB', ' ')
        output = int(number) * 1024 * 1024
    if 'GB' in bytes:
        number = bytes.replace('GB', ' ')
        output = int(number) * 1024 * 1024 * 1024
    return output


class ComputeNode:
    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name
    def set_type(self, type):
        self.__type = type

    def get_type(self):
        return self.__type

    def set_disk_size(self, disk_size):
        disk_size = convert_bytes(disk_size)
        self.__disk_size = size(disk_size, system=iec)

    def get_disk_size(self):
        return self.__disk_size

    def set_num_cpu(self, cpu):
        self.__cpu = cpu

    def get_num_cpu(self):
        return self.__cpu

    def set_mem_size(self, mem_size):
        if mem_size is not None:
            mem_size = convert_bytes(mem_size)
            self.__mem_size = size(mem_size, system=iec)
        if mem_size is None:
            self.__mem_size = mem_size

    def get_mem_size(self):
        return self.__mem_size

    def set_gpu_model(self, model):
        self.__model = model

    def get_gpu_model(self):
        return self.__model

    def set_gpu_dedicated(self, dedicated):
        self.__dedicated = dedicated

    def get_gpu_dedicated(self):
        return self.__dedicated

    def set_ip(self, ip):
        self.__ip = ip

    def get_ip(self):
        return self.__ip

    def set_relationship(self, relationship):
        self.__relationship = relationship

    def get_relationship(self):
        return self.__relationship

    def set_os(self, os):
        self.__os = os

    def get_os(self):
        return self.__os

    def set_architecture(self, arch):
        self.__arch = arch

    def get_architecture(self):
        return self.__arch

    def set_wifi_antenna(self, wifi):
        self.__wifi_antenna = wifi

    def get_wifi_antenna(self):
        return self.__wifi_antenna


class Resource:
    def set_disk(self, disk_size):
        self.__disk_size = disk_size

    def get_disk(self):
        return self.__disk_size

    def set_cpu(self, cpu):
        self.__cpu = cpu

    def get_cpu(self):
        return self.__cpu

    def set_mem(self, mem_size):
        self.__mem_size = mem_size

    def get_mem(self):
        return self.__mem_size

    def set_os(self, os):
        self.__os = os

    def get_os(self):
        return self.__os

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_gpu_model(self, model):
        self.__model = model

    def get_gpu_model(self):
        return self.__model

    def set_gpu_dedicated(self, dedicated):
        self.__dedicated = dedicated

    def get_gpu_dedicated(self):
        return self.__dedicated

    def set_wifi_antenna(self, wifi):
        self.__wifi_antenna = wifi

    def get_wifi_antenna(self):
        return self.__wifi_antenna

    def set_arch(self, arch):
        self.__arch = arch

    def get_arch(self):
        return self.__arch


