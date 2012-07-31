from twisted.protocols.basic import LineReceiver
from twisted.internet.threads import deferToThread
from twisted.internet import reactor

import sys

try:
    import msvcrt
except ImportError:
    pass  # Not Windows


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
            def getWinInput():
                if msvcrt.kbhit():
                    char = msvcrt.getche()
                    if char == "\r":
                        sys.__stdout__.write("\n")
                        char += "\n"
                    return char

            def getInput():
                if msvcrt == None:
                    return sys.stdin.readline()
                else:
                    return getWinInput()  # reactor.callFromThread(getWinInput)

            def gotInput(data):
                def sendData(data):
                    self.protocol.dataReceived(data)

                if data:
                    reactor.callFromThread(sendData, data)
                if self.protocol != None:
                    self.__worker = None
                    self.start()

            worker = deferToThread(getInput)
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
