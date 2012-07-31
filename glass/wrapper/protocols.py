from twisted.protocols.basic import LineReceiver
from twisted.python import log

from ..stdio.protocols import StandardIORelayProtocol


class WrapperClientProtocol(LineReceiver):
    def connectionMade(self):
        log.msg("Connected to master.")
        self.stdio = StandardIORelayProtocol(self)
        self.sendLine("hello")

    def connectionLost(self, reason):
        self.stdio.transport.loseConnection()

    def lineReceived(self, data):
        print data
