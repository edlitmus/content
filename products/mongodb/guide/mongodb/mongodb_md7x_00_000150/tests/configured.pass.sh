#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
maxIncomingConnections: 100
EOF
