#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
CAFile: /etc/ssl/mongodb-ca.pem
EOF
