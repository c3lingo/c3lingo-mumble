#!/bin/sh

gencert() {
  CN="$1"
  cat >.openssl.cnf <<EOF
[ req ]
prompt = no
distinguished_name = req_distinguished_name

[ req_distinguished_name ]
O = c3lingo
CN = ${CN}
emailAddress = info@c3lingo.org
EOF
  [ ! -f certs/${CN}-key.pem ] && \
  openssl req -x509 -newkey rsa:4096 -days 365 -nodes -config .openssl.cnf \
    -keyout certs/${CN}-key.pem \
    -out certs/${CN}-cert.pem
  openssl pkcs12 -export -passout pass: \
    -out certs/${CN}.p12 \
    -inkey certs/${CN}-key.pem \
    -in certs/${CN}-cert.pem
}

for i in adams borg clarke dijkstra eliza; do
  for j in 0 1 2; do
    gencert "$i-$j"
  done
done

gencert test

rm .openssl.cnf
