from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ProcessProtocol
from twisted.internet import reactor
from twisted.python import log

from .updater import updateFromManifests

import os


class EvalServerProtocol(LineReceiver):
    def __init__(self):
        self.serverId = None

    def lineReceived(self, data):
        if self.serverId == None:
            if data not in self.factory.wrapperClientFactory.serverEval:
                self.serverId = data
                self.factory.wrapperClientFactory.serverEval[self.serverId] = self

    def connectionLost(self, reason):
        if self.serverId != None and self.serverId in self.factory.wrapperClientFactory.serverEval:
            if self.factory.wrapperClientFactory.serverEval[self.serverId] is self:
                del self.factory.wrapperClientFactory.serverEval[self.serverId]


class ServerProcessProtocol(ProcessProtocol, LineReceiver):
    def __init__(self, wrapperClient, serverId):
        self.wrapperClient = wrapperClient
        self.serverId = serverId

    def connectionMade(self):
        self.wrapperClient.serverProcesses[self.serverId] = self
        self.transport.disconnecting = False  # Hack to make LineReceiver work

    def connectionLost(self, reason):
        self.wrapperClient.setServerState(self.serverId, self.wrapperClient.STATE_STOPPED)

        if self.serverId in self.factory.wrapperClientFactory.serverProcesses:
            if self.factory.wrapperClientFactory.serverProcesses[self.serverId] is self:
                del self.factory.wrapperClientFactory.serverProcesses[self.serverId]

    def outReceived(self, data):
        self.dataReceived(data)

    def lineReceived(self, data):
        self.wrapperClient.sendLine("log %s %s" % (self.serverId, data))


class WrapperClientProtocol(LineReceiver):
    def setServerState(self, id, state):
        self.factory.setServerState(id, state)

    def connectionMade(self):
        log.msg("Connected to master.")
        self.sendLine("hello")
        self.factory.protocolInstance = self
        self.processQueue()

    def connectionLost(self, reason):
        self.factory.protocolInstance = None

    def processQueue(self):
        while self.factory.queue:
            self.sendLine(self.factory.queue.pop())

    def lineReceived(self, data):
        data = data.split(" ")

        name = data[0]
        args = data[1:]

        cmd = getattr(self, "cmd_" + name, None)

        if cmd != None:
            cmd(*args)  # Note: commands should take a wildcard *args, in order to not crash if there are extra arguments

    def cmd_hello(self, *args):
        self.cmd_list_servers()

    def cmd_eval(self, server_id=None, *cmd):
        cmd = " ".join(cmd)

        if server_id in self.factory.serverEval:
            self.factory.serverEval[server_id].sendLine(cmd)

    def cmd_start_server(self, server_id=None, key=None, *args):
        if server_id not in self.factory.servers:
            self.sendLine("start_server_response_fail %s not_found" % server_id)
            return

        state = self.factory.serverState(server_id)
        if state != self.factory.STATE_STOPPED:
            self.sendLine("start_server_response_fail %s incorrect_state %s" % (server_id, state))
            return

        self.setServerState(server_id, self.factory.STATE_STARTING)

        serverConf = self.factory.servers[server_id]
        directory = serverConf['directory']
        deferredUpdater = updateFromManifests(directory, *serverConf['manifests'])

        @deferredUpdater.addCallback
        def doneUpdating(result):
            if not os.path.exists(directory + "config/server"):
                os.makedirs(directory + "config/server")
            if not os.path.exists(directory + "Add-Ons/Server_BLGEval"):
                os.makedirs(directory + "Add-Ons/Server_BLGEval")

            with open(directory + "config/server/prefs.cs", "a") as configFile:
                configFile.write("""
                    $Pref::Server::BLGEval::Port = %i;
                    $Pref::Server::BLGEval::Identifier = %s;
                """ % (self.factory.config["eval_port"], server_id))

                if key:
                    configFile.write("""
                        export("$Pref::Server::*", "config/server/prefs.cs");
                        schedule(0, 0, setKey, "%s");
                    """ % key)
            with open(directory + "Add-Ons/Server_BLGEval/description.cs", "w"):
                pass
            with open(directory + "Add-Ons/Server_BLGEval/server.cs", "w") as addOnFile:
                addOnFile.write("""
                    function setup_BLG_eval() {
                        function BLG_eval::onConnected(%this) {
                            %this.sendLine($Pref::Server::BLGEval::Identifier)
                        }

                        function BLG_eval::onLine(%this, %line) {
                            eval(%line);
                        }

                        if (!isObject(BLG_Eval))
                            new TCPObject(BLG_Eval);

                        BLG_Eval.connect("localhost:" @ $Pref::Server::BLGEval::Port);
                    }
                """)

            serverProcess = ServerProcessProtocol(self.factory, server_id)
            reactor.spawnProcess(serverProcess,
                directory + "Blockland.exe",
                ['Blockland.exe', 'ptlaaxobimwroe', '-dedicated'],
                path=directory)

            self.setServerState(server_id, self.factory.STATE_STARTED)

    def cmd_stop_server(self, server_id=None, *args):
        if server_id not in self.factory.servers:
            self.sendLine("stop_server_response_fail %s not_found" % server_id)
            return

        state = self.factory.serverState(server_id)
        if state != self.factory.STATE_STARTED:
            self.sendLine("stop_server_response_fail %s incorrect_state %s" % (server_id, state))
            return

        if server_id in self.factory.serverProcesses:
            self.factory.serverProcesses[server_id].transport.signalProcess('KILL')
            self.setServerState(server_id, self.factory.STATE_STOPPED)

    def cmd_list_servers(self, *args):
        self.sendLine("list_servers_begin")
        for server in self.factory.servers:
            self.sendLine("list_servers %s %s %s" % (server, self.factory.serverState(server), self.factory.servers[server]['name']))
        self.sendLine("list_servers_end")
