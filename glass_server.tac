#import M2Crypto.SSL.TwistedProtocolWrapper

from twisted.application import service, internet
from twisted.internet import ssl, reactor
from twisted.web import server as web_server
from twisted.web.wsgi import WSGIResource
from twisted.python.threadpool import ThreadPool

from OpenSSL import SSL

from glass.server import factories, amqp_helpers, website
from glass import SSL_METHOD, masterCA


application = service.Application("glass_server")


amqpFactory = amqp_helpers.AmqpFactory()
amqpService = internet.TCPClient("localhost", 5672, amqpFactory)
amqpService.setServiceParent(application)


wrapperContextFactory = ssl.DefaultOpenSSLContextFactory("keys/keys/serverkey.pem", "keys/keys/servercert.crt", SSL_METHOD)
wrapperContext = wrapperContextFactory.getContext()

clientContextFactory = ssl.DefaultOpenSSLContextFactory("keys/keys/serverkey.pem", "keys/keys/servercert.crt", SSL_METHOD)
clientContext = clientContextFactory.getContext()


wrapperFactory = factories.WrapperFactory(clientContext, amqpFactory)

wrapperContext.get_cert_store().add_cert(masterCA)
wrapperContext.set_verify(
    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
    wrapperFactory.verifyCert()
)

#wrapperService = internet.TCPServer(9587, wrapperFactory)
wrapperService = internet.SSLServer(9587, wrapperFactory, wrapperContextFactory)
wrapperService.setServiceParent(application)


clientFactory = factories.ClientFactory(wrapperFactory)

#clientContext.set_verify_depth(2)
clientContext.get_cert_store().add_cert(masterCA)
#clientContext.add_client_ca(masterCA)
clientContext.set_verify(
    SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT,
    clientFactory.verifyCert()
)

clientService = internet.SSLServer(9588, clientFactory, clientContextFactory)
clientService.setServiceParent(application)


wsgiThreadPool = ThreadPool()
wsgiThreadPool.start()
reactor.addSystemEventTrigger('after', 'shutdown', wsgiThreadPool.stop)

websiteResource = WSGIResource(reactor, wsgiThreadPool, website.application)
websiteFactory = web_server.Site(websiteResource)
websiteService = internet.TCPServer(8080, websiteFactory)
websiteService.setServiceParent(application)
