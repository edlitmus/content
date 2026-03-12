#!/bin/bash
# remediation = none
mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
net:
  bindIp: 127.0.0.1
CONFEOF
