from twisted.protocols.basic import LineReceiver


class WrapperClientProtocol(LineReceiver):
    def lineReceived(self, line):
        print "Line", line
