#!/bin/bash
# remediation = none

mkdir -p /etc
cat > /etc/mongod.conf <<'CONFEOF'
security:
  authorization: enabled
  ldap:
    servers: ldap.example.com
    transportSecurity: tls
    authz:
      queryTemplate: '{USER}?memberOf?base'
CONFEOF
