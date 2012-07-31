from twisted.internet.protocol import ClientFactory

from . import protocols


class WrapperClientFactory(ClientFactory):
    protocol = protocols.WrapperClientProtocol
