#!/bin/sh

#
# Register one or more certificates with the server
#

host="$1"
admin="$2"
shift 2

for i in $@; do
  pipenv run python -m c3lingo_mumble.register --host ${host} \
    --admin ${admin} --admin_certfile=certs/${admin}-cert.pem --admin_keyfile=certs/${admin}-key.pem \
    --user=${i} --certfile=certs/${i}-cert.pem --keyfile=certs/${i}-key.pem
done
