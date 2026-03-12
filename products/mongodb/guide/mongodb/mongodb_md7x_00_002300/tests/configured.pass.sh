#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
security:
  authorization: enabled
CONFEOF
chmod 0640 /etc/mongod.conf
