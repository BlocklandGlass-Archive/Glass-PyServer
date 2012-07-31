#!/bin/sh

# Regenerates a dev PKI

rm -r keys
mkdir keys

export KEY_TEMP_PASS=pass:abcd

function sign_key {
	touch keys/database.txt
	if [ ! -e keys/serial.txt ]; then
		echo 02 > keys/serial.txt
	fi
	openssl ca -cert keys/${2}cert.pem -keyfile keys/${2}key.pem -in keys/${1}cert.csr -out keys/${1}cert.pem -config ca.conf -name ca_${1} -md sha1 -batch -outdir keys ${3}
}


openssl req -newkey rsa:2048 -keyout keys/serverkey.pem -outform PEM -out keys/servercert.csr -outform PEM -days 1825 -config serverkey.conf
sign_key server server -selfsign
openssl x509 -in keys/servercert.pem -out keys/servercert.crt

openssl req -newkey rsa:2048 -keyout keys/wrapperkey.pem -outform PEM -out keys/wrappercert.csr -outform PEM -days 1825 -config wrapperkey.conf
sign_key wrapper server
openssl x509 -in keys/wrappercert.pem -out keys/wrappercert.crt

openssl req -newkey rsa:2048 -keyout keys/clientkey.pem -outform PEM -out keys/clientcert.csr -outform PEM -days 1825 -config clientkey.conf
sign_key client wrapper
openssl x509 -in keys/clientcert.pem -out keys/clientcert.crt