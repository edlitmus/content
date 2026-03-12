#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
net:
  tls:
    mode: requireTLS
    allowInvalidCertificates: false
    PEMKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/mongodbCA.pem
CONFEOF
