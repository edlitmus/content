#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
authenticationMechanisms: SCRAM-SHA-512
EOF
