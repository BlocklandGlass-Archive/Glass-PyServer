from twisted.protocols.basic import LineReceiver

from .verification import verifyDirectWrapperCert, verifyDirectClientCert


STATE_AUTHING = 0
STATE_OPEN = 1


class WrapperProtocol(LineReceiver):
    AUTH_FAILED = "AUTH_FAILED"
    AUTH_SUCCESS = "AUTH_SUCCESS"

    def __init__(self):
        self.state = STATE_AUTHING
        self.clients = set()
        self.id = None

    def connectionLost(self, reason):
        for i in self.clients:
            i.transport.loseConnection()
        self.factory.unregisterWrapper(self.id, self)

    def lineReceived(self, line):
        if self.id == None:
            id = verifyDirectWrapperCert(self.transport.getPeerCertificate())
            if id:
                self.id = id
                self.factory.registerWrapper(self.id, self)
            else:
                self.transport.loseConnection()
        for i in self.clients:
            i.sendLine(line)


class ClientProtocol(LineReceiver):
    AUTH_FAILED = "AUTH_FAILED"
    AUTH_SUCCESS = "AUTH_SUCCESS"

    def __init__(self):
        self.state = STATE_AUTHING
        self.wrapper = None

    def connectionLost(self, reason):
        if self.wrapper != None:
            self.wrapper.clients.remove(self)

    def lineReceived(self, line):
        if self.wrapper == None:
            wrapper = verifyDirectClientCert(self.transport.getPeerCertificate(), self.factory.wrapperFactory)
            if wrapper:
                self.wrapper = self.factory.wrapperFactory.getWrapper(wrapper)
                self.wrapper.clients.add(self)
            else:
                self.transport.loseConnection()
        self.wrapper.sendLine(line)
