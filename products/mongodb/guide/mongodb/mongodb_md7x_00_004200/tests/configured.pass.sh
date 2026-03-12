#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'EOF'
allowInvalidHostnames: false
allowInvalidCertificates: false
EOF
