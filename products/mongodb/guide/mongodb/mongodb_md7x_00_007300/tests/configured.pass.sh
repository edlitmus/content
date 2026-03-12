#!/bin/bash
# remediation = none
mkdir -p /etc /var/log/mongodb
cat > /etc/mongod.conf <<'CONFEOF'
systemLog:
  logRotate: reopen

auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/auditLog.json
CONFEOF
