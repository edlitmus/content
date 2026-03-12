#!/bin/bash
# remediation = none
mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
security:
  authorization: enabled

net:
  tls:
    mode: requireTLS
CONFEOF
chmod 640 /etc/mongod.conf
