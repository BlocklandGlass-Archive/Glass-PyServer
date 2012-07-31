from twisted.protocols.basic import LineReceiver


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
        if   self.state == STATE_AUTHING:
            try:
                self.id = line
                self.factory.registerWrapper(self.id, self)  # Currently using a naive "believe whatever they say auth strategy, should be fixed up later"

                self.state = STATE_OPEN
                self.sendLine(self.AUTH_SUCCESS)
            except:  # Authentication failed
                self.sendLine(self.AUTH_FAILED)
        elif self.state == STATE_OPEN:
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
        if   self.state == STATE_AUTHING:
            wrapper = self.factory.wrapperFactory.getWrapper(line)
            if wrapper != None:
                self.wrapper = wrapper
                self.wrapper.clients.add(self)
                self.state = STATE_OPEN
                self.sendLine(self.AUTH_SUCCESS)
            else:  # Authentication failed
                self.sendLine(self.AUTH_FAILED)
        elif self.state == STATE_OPEN:
            self.wrapper.sendLine(line)
