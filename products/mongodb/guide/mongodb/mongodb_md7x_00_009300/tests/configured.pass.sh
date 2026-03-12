#!/bin/bash
# remediation = none
# This test mocks a dpkg status entry indicating mongodb-org 7.0.0 is installed.

mkdir -p /var/lib/dpkg
cat >> /var/lib/dpkg/status <<'DPKGEOF'

Package: mongodb-org
Status: install ok installed
Priority: optional
Architecture: amd64
Installed-Size: 0
Maintainer: MongoDB <packaging@mongodb.com>
Version: 7.0.0
Description: MongoDB open source document-oriented database system (metapackage)
DPKGEOF
