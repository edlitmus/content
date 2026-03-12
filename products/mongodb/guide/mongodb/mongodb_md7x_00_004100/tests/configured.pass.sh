#!/bin/bash
# remediation = none

mkdir -p /etc /etc/ssl
# Write a mongod.conf that references the PEM key file path
cat > /etc/mongod.conf <<'CONFEOF'
net:
  tls:
    mode: requireTLS
    PEMKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/mongodbCA.pem
CONFEOF
# Create the PEM key file with mode 0600 (rw-------)
touch /etc/ssl/mongodb.pem
chmod 0600 /etc/ssl/mongodb.pem
