from twisted.application import service, internet
from twisted.internet import ssl

from glass.wrapper import factories

import json
import os

if not os.path.exists("wrapper"):
    os.makedirs("wrapper")
if os.path.exists("wrapper/config.json"):
    with open("wrapper/config.json") as configFile:
        config = json.load(configFile)
else:
    config = {}
config["master_ip"] = config.get("master_ip", "localhost")
config["master_port"] = config.get("master_port", 9587)
config["eval_port"] = config.get("eval_port", 9555)
with open("wrapper/config.json", "w") as configFile:
    json.dump(config, configFile)

application = service.Application("glass_wrapper")

wrapperFactory = factories.WrapperClientFactory()
wrapperService = internet.SSLClient(config["master_ip"], config["master_port"], wrapperFactory, factories.WrapperClientContextFactory())
wrapperService.setServiceParent(application)

evalServerFactory = factories.EvalServerFactory(wrapperFactory)
evalServerService = internet.TCPServer("localhost", config["eval_port"], evalServerFactory)
