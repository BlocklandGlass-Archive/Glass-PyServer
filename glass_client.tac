from twisted.application import service, internet
from twisted.internet import ssl

from glass.client import factories


application = service.Application("glass_client")

clientFactory = factories.ClientClientFactory()
clientService = internet.SSLClient("localhost", 9588, clientFactory, ssl.ClientContextFactory())
clientService.setServiceParent(application)
