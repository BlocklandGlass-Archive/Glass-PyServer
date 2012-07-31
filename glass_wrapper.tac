from twisted.application import service, internet
from twisted.internet import ssl

from glass.wrapper import factories


application = service.Application("glass_wrapper")

wrapperFactory = factories.WrapperClientFactory()
wrapperService = internet.SSLClient("localhost", 9587, wrapperFactory, ssl.ClientContextFactory())
wrapperService.setServiceParent(application)
