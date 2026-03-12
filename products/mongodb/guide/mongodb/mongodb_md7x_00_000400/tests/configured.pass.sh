#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
auditLog:
auditAuthorizationSuccess: true
EOF
