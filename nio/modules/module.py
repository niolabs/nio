from sys import maxsize


class Module(object):

    def initialize(self, context):
        pass

    def finalize(self):
        pass

    def get_module_order(self):
        return maxsize
