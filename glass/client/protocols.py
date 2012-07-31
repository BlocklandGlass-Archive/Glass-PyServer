from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Protocol
from twisted.python import log

from ..stdio.protocols import StandardIORelayProtocol


class ClientClientProtocol(LineReceiver):
    def connectionMade(self):
        log.msg("Connected to master.")
        self.stdio = StandardIORelayProtocol(self)

    def connectionLost(self, reason):
        self.stdio.transport.loseConnection()

    def lineReceived(self, data):
        print data
