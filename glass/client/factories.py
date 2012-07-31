from twisted.internet.protocol import ClientFactory
from twisted.python import log
from twisted.internet import reactor

from . import protocols


class ClientClientFactory(ClientFactory):
    protocol = protocols.ClientClientProtocol

    def clientConnectionLost(self, connector, reason):
        if reactor.running:
            log.msg("Disconnected from master, stopping.")
            reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        if reactor.running:
            log.msg("Connection to master failed, stopping.")
            reactor.stop()
