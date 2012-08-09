from twisted.internet.protocol import ReconnectingClientFactory, Factory
from twisted.internet import ssl

from . import protocols
from ..constants import SSL_METHOD

import json
import os


class WrapperClientContextFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.use_certificate_file('keys/keys/wrappercert.crt')
        ctx.use_privatekey_file('keys/keys/wrapperkey.pem')
        return ctx


class EvalServerFactory(Factory):
    protocol = protocols.EvalServerProtocol

    def __init__(self, wrapperClientFactory):
        self.wrapperClientFactory = wrapperClientFactory


class WrapperClientFactory(ReconnectingClientFactory):
    protocol = protocols.WrapperClientProtocol

    STATE_STOPPED = "stopped"
    STATE_STARTING = "starting"
    STATE_STARTED = "started"

    def serverState(self, id):
        return self.serverStates.get(id, self.STATE_STOPPED)

    @property
    def servers(self):
        if 'servers' not in self.config:
            self.config['servers'] = {}
        return self.config['servers']

    def startFactory(self):
        self.serverSockets = {}
        self.serverProcesses = {}
        self.serverStates = {}
        self.serverEval = {}

        self.queue = []
        self.protocolInstance = None

        if os.path.exists("wrapper/config.json"):
            with open("wrapper/config.json") as file:
                self.config = json.load(file)
        else:
            self.config = {}

    def stopFactory(self):
        if not os.path.exists("wrapper"):
            os.makedirs("wrapper")
        with open("wrapper/config.json", "w") as file:
            json.dump(self.config, file)

    def sendLine(self, msg):
        self.queue.append(msg)
        if self.protocolInstance != None:
            self.protocolInstance.processQueue()

    def setServerState(self, id, state):
        self.serverStates[id] = state
        self.sendLine("server_state %s %s" % (id, state))
