#!/bin/bash
# remediation = none
# Create a stub mongod binary owned by root with mode 0755.

mkdir -p /usr/bin
install -o root -g root -m 0755 /dev/null /usr/bin/mongod
