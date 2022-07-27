class CloudFramework:
    def set_type(self, type):
        self.__type = type

    def get_type(self):
        return self.__type

    def set_secret_name(self, secret_name):
        self.__secret_name = secret_name

    def get_secret_name(self):
        return self.__secret_name

    def set_application(self, app):
        self._app = app

    def get_application(self):
        return self._app

    def set_literals(self, literals):
        self.__literals = literals

    def get_literals(self):
        return self.__literals

    def set_resources(self, resources):
        self.__resources = resources

    def get_resources(self):
        return self.__resources

    def set_order(self, order):
        self.__order = order

    def get_order(self):
        return self.__order

    def set_target(self, target):
        self.__target = target

    def set_relationship(self, relationship):
        self.__relationship = relationship

    def get_relationship(self):
        return self.__relationship

    def set_actions(self, actiolist):
        self.__actionlist = actiolist

    def get_actions(self):
        return self.__actionlist

    def set_workflows(self, workflowlist):
        self.__workflowlist = workflowlist

    def get_workflows(self):
        return self.__workflowlist
