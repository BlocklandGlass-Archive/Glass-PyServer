from twisted.internet.protocol import ClientFactory
from twisted.python import log
from twisted.internet import reactor, ssl

from . import protocols
from ..constants import SSL_METHOD


class WrapperClientContextFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('keys/keys/wrappercert.crt')
        ctx.use_privatekey_file('keys/keys/wrapperkey.pem')
        return ctx


class WrapperClientFactory(ClientFactory):
    protocol = protocols.WrapperClientProtocol

    def clientConnectionLost(self, connector, reason):
        if reactor.running:
            log.msg("Disconnected from master, stopping.")
            reactor.stop()

    def clientConnectionFailed(self, connector, reason):
        if reactor.running:
            log.msg("Connection to master failed, stopping.")
            reactor.stop()
