from OpenSSL.SSL import SSLv3_METHOD
from OpenSSL import crypto


SSL_METHOD = SSLv3_METHOD

masterCA = crypto.load_certificate(crypto.FILETYPE_PEM, open("keys/keys/servercert.pem").read())
