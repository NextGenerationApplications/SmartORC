class Container:
    def set_relatioship(self, host):
        self.__host = host

    def get_relationship(self):
        return self.__host

    def set_type(self, type):
        self.__type = type

    def get_type(self):
        return self.__type

    def set_host(self, host):
        self.__host = host

    def get_host(self):
        return self.__host

    def set_port(self, port):
        self.__port = port

    def get_port(self):
        return self.__port

    def set_name(self, name):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_tier(self, tier):
        self.__tier = tier

    def get_tier(self):
        return self.__tier

    def set_image_pull_policy(self, policy):
        self.__policy = policy

    def get_image_pull_policy(self):
        return self.__policy

    def set_username(self, username):
        self.__username = username

    def get_username(self):
        return self.__username

    def set_uservalue(self, uservalue):
        self.__uservalue = uservalue

    def get_uservalue(self):
        return self.__uservalue

    def set_passwordname(self, passwordname):
        self.__passwordname = passwordname

    def get_passwordname(self):
        return self.__passwordvalue

    def set_secretname(self, secretname):
        self.__secretname = secretname

    def get_secretname(self):
        return self.__secretname

    def set_secretkey(self, secretkey):
        self.__secretkey = secretkey

    def get_secretkey(self):
        return self.__secretkey

    def set_volumeMounts_name(self, volumemounts_name):
        self.__volumemounts_name = volumemounts_name

    def get_volumeMounts_name(self):
        return self.__volumemounts_name

    def set_volumeMounts_path(self, volumemounts_path):
        self.__volumemounts_path = volumemounts_path

    def get_volumeMounts_path(self):
        return self.__volumemounts_path

    def set_volumes_name(self, volumes_name):
        self.__volumes_name = volumes_name

    def get_volumes_name(self):
        return self.__volumes_name

    def set_volumes_claimname(self, volumes_claimname):
        self.__volumes_claimname = volumes_claimname

    def get_volumes_claimname(self):
        return self.__volumes_claimname

    def set_env(self, env):
        self.__env = env

    def get_env(self):
        return self.__env

    def set_namespace(self, namespace):
        self.__namespace = namespace

    def get_namespace(self):
        return self.__namespace

    def set_application(self, app):
        self.__app = app

    def get_application(self):
        return self.__app

    def set_service(self, service):
        self.__service = service

    def get_service(self):
        return self.__service

    def set_ingress(self, ingress):
        self.__ingress = ingress

    def get_ingress(self):
        return self.__ingress

    def set_image(self, images):
        self.__images = images

    def get_image(self):
        return self.__images

    def set_internal(self, boolean):
        self.__internal = boolean

    def get_internal(self):
        return self.__internal

    def set_unit(self, unit):
        self.__unit = unit

    def get_unit(self):
        return self.__unit

    def set_flavor(self, flavor):
        self.__flavor = flavor

    def get_flavor(self):
        return self.__flavor

    def set_dependency(self, dependency):
        self.__dependency = dependency

    def get_dependency(self):
        return self.__dependency
