#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
redactClientLogData: true
EOF
