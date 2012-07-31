def verifyMasterCert(x509):
    return (x509.get_issuer().O == "BLG.Master" and
            x509.get_subject().O == "BLG.Master")


def verifyDirectWrapperCert(x509):
    return (x509.get_issuer().O == "BLG.Master" and
            x509.get_subject().O == "BLG.Wrapper" and
            x509.get_subject().OU)


def verifyWrapperCert(x509):
    return (verifyMasterCert(x509) or
            verifyDirectWrapperCert(x509))


def verifyDirectClientCert(x509, wrapperFactory):
    if (x509.get_issuer().O == "BLG.Wrapper" and
        x509.get_subject().O == "BLG.Client"):
            if wrapperFactory.getWrapper(x509.get_issuer().OU) != None:
                return x509.get_issuer().OU
    return False


def verifyClientCert(x509, wrapperFactory):
    return (verifyWrapperCert(x509) or
            verifyDirectClientCert(x509, wrapperFactory))
