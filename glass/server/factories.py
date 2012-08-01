from twisted.internet.protocol import Factory

from OpenSSL import crypto

from . import protocols
from .verification import verifyClientCert, verifyWrapperCert


class WrapperFactory(Factory):
    protocol = protocols.WrapperProtocol

    amqp_queue = "blg.server.wrapper.messages"

    def __init__(self, clientContext, amqp):
        self.wrappers = {}
        self.clientContext = clientContext
        self.amqp = amqp

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

    def amqpGotMessage(self, msg):
        id = msg[-1]
        body = msg.content.body
        self.getWrapper(id).sendLine(body)

    def registerWrapper(self, id, wrapper):
        if not id:
            raise ValueError("Invalid wrapper id")

        if id in self.wrappers:
            self.wrappers[id].transport.loseConnection()
        self.wrappers[id] = wrapper
        self.amqp.read(self.amqp_queue, id, self.amqpGotMessage, no_ack=True)  # TODO: Add proper ack tracking

    def unregisterWrapper(self, id, wrapper):
        if id in self.wrappers and self.wrappers[id] == wrapper:
            del self.wrappers[id]
            self.amqp.stop_reading(self.amqp_queue, id, self.amqpGotMessage)

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
