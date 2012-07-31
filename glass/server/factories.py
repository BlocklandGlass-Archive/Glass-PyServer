from twisted.internet.protocol import Factory

from OpenSSL import crypto

from . import protocols
from .verification import verifyClientCert, verifyWrapperCert


class WrapperFactory(Factory):
    protocol = protocols.WrapperProtocol

    def __init__(self, clientContext):
        self.wrappers = {}
        self.clientContext = clientContext

    def verifyCert(self):
        def inner(connection, x509, errnum, errdepth, ok):
            if ok and verifyWrapperCert(x509):
                try:
                    self.clientContext.get_cert_store().add_cert(x509)
                except crypto.Error:
                    pass
                return True
            return False
        return inner

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
    protocol = protocols.ClientProtocol

    def __init__(self, wrapperFactory):
        self.wrapperFactory = wrapperFactory

    def verifyCert(self):
        def inner(connection, x509, errnum, errdepth, ok):
            if ok and verifyClientCert(x509, self.wrapperFactory):
                return True
            return False
        return inner
