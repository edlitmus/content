#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
security:
  authorization: enabled
setParameter:
  authenticationMechanisms: SCRAM-SHA-256,SCRAM-SHA-512
CONFEOF
