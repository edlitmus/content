#!/bin/bash
# platform = MongoDB
# Remediation for MD7X-00-000200: Configure MongoDB for external authentication
# MongoDB must integrate with an organization-level authentication/access mechanism

# Configuration file location
MONGOD_CONFIG="/etc/mongod.conf"

# Check if mongod.conf exists
if [ ! -f "$MONGOD_CONFIG" ]; then
    echo "Error: MongoDB configuration file not found at $MONGOD_CONFIG"
    exit 1
fi

# Backup original file
cp "$MONGOD_CONFIG" "${MONGOD_CONFIG}.bak.$(date +%s)"

# Configure external authentication mechanism
# This example configures LDAP - adjust as needed for your environment

# Add security section if it doesn't exist
if ! grep -q "^security:" "$MONGOD_CONFIG"; then
    cat >> "$MONGOD_CONFIG" << 'EOF'

security:
  ldap:
    servers:
      - "ldap.example.com"
  authenticationMechanisms:
      - SCRAM-SHA-1
      - GSSAPI
      - PLAIN
      - MONGODB-OIDC
EOF
else
    # Add LDAP configuration to existing security section
    if ! grep -q "servers:" "$MONGOD_CONFIG"; then
        sed -i '/^security:/a\  ldap:\n    servers:\n      - "ldap.example.com"' "$MONGOD_CONFIG"
    fi
    
    # Ensure authenticationMechanisms includes external mechanisms
    if ! grep -q "authenticationMechanisms:" "$MONGOD_CONFIG"; then
        sed -i '/^security:/a\  authenticationMechanisms:\n      - SCRAM-SHA-1\n      - GSSAPI\n      - PLAIN\n      - MONGODB-OIDC' "$MONGOD_CONFIG"
    fi
fi

# Restart MongoDB to apply changes
systemctl restart mongod

echo "MongoDB configured for external authentication. Please verify LDAP settings are appropriate for your environment."
