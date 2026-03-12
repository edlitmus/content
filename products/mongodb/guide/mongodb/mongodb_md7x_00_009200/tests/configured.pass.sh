#!/bin/bash
# remediation = none
mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
net:
  tls:
    mode: requireTLS
    disabledProtocols: TLS1_0,TLS1_1
CONFEOF
