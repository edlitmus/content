#!/bin/bash
# remediation = none
mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
systemLog:
  destination: syslog

auditLog:
  destination: syslog
CONFEOF
