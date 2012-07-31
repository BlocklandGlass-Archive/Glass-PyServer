from twisted.internet.protocol import Factory

from . import protocols


class WrapperFactory(Factory):
    protocol = protocols.WrapperProtocol

    def __init__(self):
        self.wrappers = {}

    def registerWrapper(self, id, wrapper):
        if not id:
            raise ValueError("Invalid wrapper id")

        if id in self.wrappers:
            self.wrappers[id].transport.loseConnection()
        self.wrappers[id] = wrapper

    def unregisterWrapper(self, id, wrapper):
        if id in self.wrappers and self.wrappers[id] == wrapper:
            del self.wrappers[id]

    def getWrapper(self, id):
        if id in self.wrappers:
            return self.wrappers[id]


class ClientFactory(Factory):
    def __init__(self, wrapperFactory):
        self.wrapperFactory = wrapperFactory

    protocol = protocols.ClientProtocol
