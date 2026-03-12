#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
mode: requireTLS
allowInvalidCertificates: false
allowConnectionsWithoutCertificates: false
EOF
