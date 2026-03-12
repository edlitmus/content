#!/bin/bash
# remediation = none
mkdir -p /etc /var/log/mongodb
cat > /etc/mongod.conf <<'CONFEOF'
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/auditLog.json
CONFEOF
