from twisted.internet.protocol import ClientFactory
from twisted.python import log
from twisted.internet import reactor, ssl

from . import protocols
from ..constants import SSL_METHOD


class ClientClientContextFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('keys/keys/clientcert.crt')
        ctx.use_privatekey_file('keys/keys/clientkey.pem')
        return ctx


class ClientClientFactory(ClientFactory):
    protocol = protocols.ClientClientProtocol

    def clientConnectionLost(self, connector, reason):
        if reactor.running:
            log.msg("Disconnected from master, stopping. Press enter to exit.")
            reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        if reactor.running:
            log.msg("Connection to master failed, stopping.")
            reactor.stop()
