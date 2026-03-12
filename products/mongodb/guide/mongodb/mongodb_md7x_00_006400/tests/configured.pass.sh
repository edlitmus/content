#!/bin/bash
# remediation = none
mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
security:
  enableEncryption: true
CONFEOF
