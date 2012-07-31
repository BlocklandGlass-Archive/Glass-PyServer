from twisted.application import service, internet
from twisted.internet import ssl

from OpenSSL import SSL

from glass.server import factories
from glass import SSL_METHOD


application = service.Application("glass_server")


wrapperContextFactory = ssl.DefaultOpenSSLContextFactory("keys/serverkey.pem", "keys/servercert.crt", SSL_METHOD)
wrapperContextFactory.getContext().set_verify(
    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
    factories.verifyWrapperCert
)

wrapperFactory = factories.WrapperFactory()
wrapperService = internet.TCPServer(9587, wrapperFactory)
#wrapperService = internet.SSLServer(9587, wrapperFactory, wrapperContextFactory)
wrapperService.setServiceParent(application)


clientContextFactory = ssl.DefaultOpenSSLContextFactory("keys/serverkey.pem", "keys/servercert.crt", SSL_METHOD)
#clientContextFactory.getContext().set_verify(
#    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
#    factories.verifyClientCert
#)

clientFactory = factories.ClientFactory(wrapperFactory)
clientService = internet.SSLServer(9588, clientFactory, clientContextFactory)
clientService.setServiceParent(application)
