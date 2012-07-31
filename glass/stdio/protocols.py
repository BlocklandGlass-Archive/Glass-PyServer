from twisted.protocols.basic import LineReceiver
from twisted.internet.threads import deferToThread
from twisted.internet import reactor


class StandardIO(object):
    def __init__(self, protocol):
        self.protocol = protocol
        self.__worker = None
        self.start()

    @property
    def disconnecting(self):
        return self.protocol == None

    def start(self):
        if self.__worker == None:
            def gotInput(line):
                def sendData(line):
                    self.protocol.dataReceived(line + "\r\n")

                if line:
                    reactor.callFromThread(sendData, line)
                if self.protocol != None:
                    self.__worker = None
                    self.start()

            worker = deferToThread(raw_input)
            self.__worker = worker
            worker.addCallback(gotInput)

    def loseConnection(self):
        self.protocol = None


class StandardIORelayProtocol(LineReceiver):
    def __init__(self, parent):
        self.parent = parent
        self.transport = StandardIO(self)

    def lineReceived(self, line):
        self.parent.sendLine(line)
