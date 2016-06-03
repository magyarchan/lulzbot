from pyhocon import ConfigFactory

class Config:
    def __init__(self, config = "development.conf"):
        self.conf = ConfigFactory.parse_file(config)

    def debug(self):
        print(self.conf)

    def getString(self, key):
        return self.conf.get_string(key)

    def getInt(self, key):
        return self.conf.get_int(key)

