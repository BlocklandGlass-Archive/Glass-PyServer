Glass-PyServer
==============

BlocklandGlass server written in Python 2.


Authentication
--------------

Authentication is done using SSL client certs. There are three different types of certs (currently stored in the cert's organizationName field), BLG.Master (the master server's cert, also acts as the master CA, although these functions might be separated later), BLG.Wrapper (the wrapper's cert as well as the CA for the "real clients" (the administrators)), and BLG.Client (the "real client" cert).

Once a connection is open the master server acts as a "pubsub" proxy; what the wrapper sends is sent to all of it's clients, while anything a client sends is sent back to the wrapper.


Dependencies
------------

### Server

* RabbitMQ