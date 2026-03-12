#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
net:
  tls:
    mode: requireTLS
    FIPSMode: true
    PEMKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/mongodbCA.pem
security:
  authorization: enabled
CONFEOF
