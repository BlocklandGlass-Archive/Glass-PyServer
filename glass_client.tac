from twisted.application import service, internet
from twisted.internet import ssl

from glass.client import factories

import json
import os

if not os.path.exists("client"):
    os.makedirs("client")
if os.path.exists("client/config.json"):
    with open("client/config.json") as configFile:
        config = json.load(configFile)
else:
    config = {}
config["master_ip"] = config.get("master_ip", "localhost")
config["master_port"] = config.get("master_port", 9588)
with open("client/config.json", "w") as configFile:
    json.dump(config, configFile)


application = service.Application("glass_client")

clientFactory = factories.ClientClientFactory()
clientService = internet.SSLClient(config["master_ip"], config["master_port"], clientFactory, factories.ClientClientContextFactory())
clientService.setServiceParent(application)
