class Ubuntu:

    def wifi(self):
        raise NotImplementedError

    def static_network(self):
        raise NotImplementedError

    def dhcp(self):
        raise NotImplementedError

    def keyboard(self):
        raise NotImplementedError

    def locale(self):
        raise NotImplementedError

    def hostname(self):
        raise NotImplementedError

    def etc_hosts(self):
        raise NotImplementedError

    def startup(self):
        raise NotImplementedError

    def cloud_config(self):
        raise NotImplementedError

    def set_key(self):
        raise NotImplementedError

    def add_key(self):
        raise NotImplementedError

    def permissions(self):
        raise NotImplementedError

    def add_user(self):
        raise NotImplementedError

    def enable_ssh(self):
        raise NotImplementedError

    def disable_password(self):
        raise NotImplementedError

    #
    # POST INSTALATION
    #
    def firmware(self):
        raise NotImplementedError
