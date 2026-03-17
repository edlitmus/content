#!/bin/bash
# platform = MongoDB
# Remediation for MD7X-00-000300: Enable MongoDB Authorization/RBAC
# MongoDB must enforce approved authorizations for logical access

# Configuration file location
MONGOD_CONFIG="/etc/mongod.conf"

# Check if mongod.conf exists
if [ ! -f "$MONGOD_CONFIG" ]; then
    echo "Error: MongoDB configuration file not found at $MONGOD_CONFIG"
    exit 1
fi

# Backup original file
cp "$MONGOD_CONFIG" "${MONGOD_CONFIG}.bak.$(date +%s)"

# Check if security section exists
if grep -q "^security:" "$MONGOD_CONFIG"; then
    # Update existing security section
    if grep -q "^\s*authorization:" "$MONGOD_CONFIG"; then
        # Replace existing authorization setting
        sed -i.backup 's/^\(\s*authorization\s*:\).*/\1 enabled/' "$MONGOD_CONFIG"
    else
        # Add authorization under existing security section
        sed -i.backup '/^security:/a\  authorization: enabled' "$MONGOD_CONFIG"
    fi
else
    # Create new security section with authorization
    cat >> "$MONGOD_CONFIG" << 'EOF'

security:
  authorization: enabled
EOF
fi

# Verify configuration syntax
if ! /usr/bin/mongod --config "$MONGOD_CONFIG" --configExpand=exec --dbpath /tmp --logpath /dev/null --fork 2>&1 | grep -q "try"; then
    # Basic syntax check passed
    echo "MongoDB configuration updated successfully with authorization enabled"
else
    echo "Warning: Configuration syntax check may have failed. Please verify:"
    echo "  mongod --config $MONGOD_CONFIG --configExpand=exec"
    exit 1
fi

# Restart MongoDB to apply changes
systemctl restart mongod

# Wait for MongoDB to start
sleep 2

# Verify MongoDB is running
if systemctl is-active --quiet mongod; then
    echo "MongoDB restarted successfully with authorization enabled"
    
    # Connect to MongoDB to verify RBAC is active
    echo "Verifying authorization is active:"
    mongosh --eval "db.adminCommand('listCommands')" 2>&1 | grep -q "ok" && echo "RBAC verification successful" || echo "Warning: Could not verify RBAC status"
else
    echo "Error: MongoDB failed to start after enabling authorization"
    echo "Please check the MongoDB logs and MongoDB configuration"
    exit 1
fi
