# MongoDB STIG OVAL Remediation Matrix

This document classifies all 35 rules that were incorrectly mapped to the generic
`authorization: enabled` config check. Each rule is assigned one of four actions:

| Action | Meaning |
|--------|---------|
| **KEEP** | `authorization: enabled` is the correct primary check for this control's intent |
| **REWRITE OVAL** | The rule requires a control-specific check — config key, file permissions, or package version |
| **HYBRID** | Partial OVAL check plus an OCIL questionnaire for the remainder |
| **CONVERT TO OCIL** | No machine-verifiable check possible; becomes a manual/procedural questionnaire |

---

## Summary Counts

| Action | Count |
|--------|-------|
| KEEP | 8 |
| REWRITE OVAL | 15 |
| HYBRID | 4 |
| CONVERT TO OCIL | 8 |
| **Total** | **35** |

---

## HIGH Severity Rules (6 total — all need action)

| Rule ID | Title | Current Pattern | Action | Correct Pattern / Rationale |
|---------|-------|-----------------|--------|-----------------------------|
| `mongodb_md7x_00_000200` | MongoDB must integrate with an organization-level authentication/access mechanism providing account management and automation for all users, groups, roles, and any other principals. | `authorization: enabled` | **REWRITE OVAL** | Check `security.ldap.transportSecurity:` exists OR `security.authenticationMechanisms` contains `PLAIN`, `GSSAPI`, or `MONGODB-OIDC` in mongod.conf. The control specifically requires *external* (org-level) identity provider integration, not just local RBAC. |
| `mongodb_md7x_00_000300` | MongoDB must enforce approved authorizations for logical access to information and system resources in accordance with applicable access control policies. | `authorization: enabled` | **KEEP** ✓ | `authorization: enabled` directly enables MongoDB RBAC, which IS the access control mechanism implementing this requirement. |
| `mongodb_md7x_00_002700` | MongoDB software installation account must be restricted to authorized users. | `authorization: enabled` | **REWRITE OVAL** | `unix:file_test` on `/usr/bin/mongod`: owned by root (uid=0, gid=0), mode 755. If the binary is root-owned and not world-writable, only authorized accounts (root/sudo) can modify or replace it. |
| `mongodb_md7x_00_004100` | MongoDB must enforce authorized access to all PKI private keys stored/used by MongoDB. | `authorization: enabled` | **REWRITE OVAL** | Two-criterion check: (1) `net.tls.PEMKeyFile:` is configured in mongod.conf; (2) the referenced key file has mode 0600 (rw-------). Uses OVAL `local_variable` to extract the path from config, then `unix:file_test` on that extracted path. |
| `mongodb_md7x_00_005200` | MongoDB must protect the confidentiality and integrity of all information at rest. | `authorization: enabled` | **REWRITE OVAL** | Check `security.enableEncryption: true` (or `yes`) in mongod.conf. This is the MongoDB at-rest encryption configuration setting (Enterprise required). |
| `mongodb_md7x_00_008300` | MongoDB must use NSA-approved cryptography to protect classified information in accordance with the data owner's requirements. | `authorization: enabled` | **REWRITE OVAL** | Two-criterion check: (1) `net.tls.mode: requireTLS`; (2) `net.tls.FIPSMode: true`. NSA-approved = FIPS 140-2/3 validated modules, which requires both TLS enforcement and FIPS mode enabled. |
| `mongodb_md7x_00_009300` | MongoDB products must be a supported version. | `authorization: enabled` | **REWRITE OVAL** | `linux:dpkginfo_test` checking `mongodb-org` package EVR ≥ `0:7.0.0-1`. Version checking is a package-manager concern, completely unrelated to the authorization config key. |

---

## MEDIUM Severity Rules (29 total)

### REWRITE OVAL (9 rules)

| Rule ID | Title | Action | Correct Pattern / Rationale |
|---------|-------|--------|-----------------------------|
| `mongodb_md7x_00_002000` | The audit information produced by MongoDB must be protected from unauthorized access. | **REWRITE OVAL** | `unix:file_test` on `/var/log/mongodb/` directory: mode ≤ 750, owned by mongod. The audit *log* protection requires file-system-level permissions, not a config key on access control. |
| `mongodb_md7x_00_002300` | MongoDB must protect its audit features from unauthorized access. | **REWRITE OVAL** | `unix:file_test` on `/etc/mongod.conf`: mode 600 (rw-------), owned by mongod. The audit configuration file must itself be access-controlled. |
| `mongodb_md7x_00_002800` | Database software, including DBMS configuration files, must be stored in dedicated directories, or DASD pools, separate from the host OS and other applications. | **REWRITE OVAL** | `unix:file_test` on `/var/lib/mongodb` (data directory): exists and is owned by mongod. ALSO `unix:file_test` on `/usr/bin/mongod` to confirm binaries are in a standard dedicated path, not co-mingled with application code. |
| `mongodb_md7x_00_003600` | MongoDB must uniquely identify and authenticate organizational users (or processes acting on behalf of organizational users). | **REWRITE OVAL** | `ind:textfilecontent54_test` checking `authenticationMechanisms:` contains `SCRAM-SHA-256`, `SCRAM-SHA-512`, `MONGODB-X509`, `GSSAPI`, or `PLAIN`. Authentication mechanisms must be explicitly configured; having authorization enabled does not guarantee authentication is required. |
| `mongodb_md7x_00_004500` | MongoDB must uniquely identify and authenticate nonorganizational users (or processes acting on behalf of nonorganizational users). | **REWRITE OVAL** | Same as `003600`: check `authenticationMechanisms:` in mongod.conf. |
| `mongodb_md7x_00_008000` | The DBMS must disable network functions, ports, protocols, and services deemed by the organization to be nonsecure, in accord with the PPSM guidance. | **REWRITE OVAL** | Check `net.tls.mode: requireTLS` in mongod.conf. PLAINTEXT listener is the "nonsecure network protocol"; `requireTLS` disables unencrypted connections. |
| `mongodb_md7x_00_008500` | MongoDB must implement cryptographic mechanisms to prevent unauthorized modification of organization-defined information at rest. | **REWRITE OVAL** | Check `security.enableEncryption: true` — identical requirement to `005200` (at-rest encryption). The OVAL check is the same. |
| `mongodb_md7x_00_008800` | MongoDB must maintain the confidentiality and integrity of information during preparation for transmission. | **REWRITE OVAL** | Check `net.tls.mode: requireTLS` AND `net.tls.allowInvalidCertificates: false`. Transmission confidentiality/integrity requires enforced TLS with valid certificates. |
| `mongodb_md7x_00_008900` | MongoDB must maintain the confidentiality and integrity of information during reception. | **REWRITE OVAL** | Same as `008800`: `net.tls.mode: requireTLS` + `net.tls.allowInvalidCertificates: false`. Reception of data over the network uses the same TLS configuration. |

### KEEP ✓ (8 rules)

| Rule ID | Title | Rationale |
|---------|-------|-----------|
| `mongodb_md7x_00_002900` | Database objects must be owned by database/DBMS principals authorized for ownership. | With RBAC enabled, only authenticated principals with `dbOwner` or higher roles can create/own objects. |
| `mongodb_md7x_00_003000` | The role(s)/group(s) used to modify database structure must be restricted to authorized users. | RBAC enabled means only principals with `dbAdmin` or `readWrite` roles can modify structure. |
| `mongodb_md7x_00_004600` | MongoDB must separate user functionality from database management functionality. | `authorization: enabled` prevents non-admin users from performing admin operations on the `admin` database. |
| `mongodb_md7x_00_005400` | Database contents must be protected from unauthorized and unintended information transfer by enforcement of a data-transfer policy. | RBAC enforces that only authorized roles can perform `find`, `aggregate`, or `mongoexport` operations. |
| `mongodb_md7x_00_006700` | MongoDB must enforce discretionary access control (DAC) policies. | MongoDB's RBAC IS the DAC mechanism. `authorization: enabled` is the correct single check. |
| `mongodb_md7x_00_006800` | MongoDB must prevent nonprivileged users from executing privileged functions. | `authorization: enabled` is the direct control gate for privileged function execution. |
| `mongodb_md7x_00_007800` | MongoDB must enforce access restrictions associated with changes to the configuration of MongoDB or database(s). | With RBAC enabled, only `dbAdminAnyDatabase` or equivalent roles can alter DB configuration. |
| `mongodb_md7x_00_002600` | (Reclassified to HYBRID — see below) | — |

### HYBRID (4 rules)

| Rule ID | Title | OVAL Part | OCIL Part |
|---------|-------|-----------|-----------|
| `mongodb_md7x_00_002600` | MongoDB must limit privileges to change software modules, to include stored procedures, functions and triggers, and links to software external to MongoDB. | `authorization: enabled` (ensures only authorized principals can create functions/views) | Manual check: verify no user outside DBA group has been granted `dbAdminAnyDatabase` or `clusterAdmin` role. MongoDB lacks stored procs but uses JS server-side functions and `$accumulator`/`$function` operators requiring role grants. |
| `mongodb_md7x_00_005500` | MongoDB must prevent unauthorized and unintended information transfer via shared system resources. | `authorization: enabled` (RBAC limits cross-database reads) | OS-level check: verify transparent huge pages are disabled and MongoDB data directory is on dedicated partition (kernel memory isolation concern, not a mongod.conf setting). |
| `mongodb_md7x_00_009100` | When updates are applied to MongoDB software, any software components that have been replaced or made unnecessary must be removed. | `unix:file_test` checking no `.old`, `.bak`, or version-tagged MongoDB binaries exist in `/usr/bin/` | Manual package audit: verify `apt list --installed | grep mongodb` shows no orphaned old-version packages. |
| `mongodb_md7x_00_012400` | MongoDB must off-load audit data to a separate log management facility. | `ind:textfilecontent54_test` checking `auditLog:` with `destination: syslog` OR `destination: file` with path outside `/var/lib/mongodb/` | Manual check: confirm syslog or Splunk/ELK integration is configured and receiving MongoDB audit events. |

### CONVERT TO OCIL (8 rules)

These controls have no machine-verifiable equivalent in mongod.conf. The current
`authorization: enabled` check creates a false positive (rule passes even when
the actual requirement is not met). These should be converted to manual questionnaires.

| Rule ID | Title | Why Not Automatable |
|---------|-------|---------------------|
| `mongodb_md7x_00_006200` | The DBMS must automatically terminate a user session after organization-defined conditions or trigger events requiring session disconnect. | MongoDB has no idle session timeout in mongod.conf. Client-side drivers and connection pools control session lifetime. Requires procedural review of application-level connection handling. |
| `mongodb_md7x_00_006400` | MongoDB must associate organization-defined types of security labels having organization-defined security label values with information in storage. | MongoDB has no native security label mechanism. Requires application-level field tagging or MongoDB Field-Level Encryption with metadata labels — cannot be checked via mongod.conf. |
| `mongodb_md7x_00_007200` | MongoDB must allocate audit record storage capacity in accordance with site audit record storage requirements. | Audit log storage sizing is an operational planning and capacity management concern, not a MongoDB configuration key. Requires site-specific administrative review. |
| `mongodb_md7x_00_007300` | MongoDB must provide a warning to appropriate support staff when allocated audit record storage volume reaches 75 percent of maximum audit record storage capacity. | Requires external monitoring infrastructure (Prometheus/Alertmanager, Datadog, AWS CloudWatch). No native 75% storage warning in MongoDB. |
| `mongodb_md7x_00_007400` | MongoDB must provide an immediate real-time alert to appropriate support staff of all audit log failures. | Requires external log monitoring pipeline. MongoDB writes audit failures to its own audit log (circular dependency). External SYSLOG + alerting stack required. |
| `mongodb_md7x_00_009000` | When invalid inputs are received, MongoDB must behave in a predictable and documented manner that reflects organizational and system objectives. | Input validation behavior is determined by MongoDB's implemented data model validation (`$jsonSchema` validators per-collection), not a global mongod.conf setting. Requires application-level schema review. |
| `mongodb_md7x_00_009200` | Security-relevant software updates to MongoDB must be installed within the time period directed by an authoritative source. | "Within N days of release" is a policy compliance check requiring patch management system integration (Qualys, Tenable, WSUS). Cannot be determined from the local system state alone. |
| `mongodb_md7x_00_012500` | MongoDB must be configured in accordance with the security configuration settings based on DOD security configuration and implementation guidance. | Omnibus "everything else" catch-all control. Requires human review of the full mongod.conf against the STIG benchmark. Automated checks for specific settings already exist as individual rules. |

---

## Implementation Priority Order

1. HIGH REWRITE: `009300`, `005200`, `008300`, `002700`, `004100`, `000200`
2. MEDIUM REWRITE: `002000`, `002300`, `003600`, `004500`, `008000`, `008500`, `008800`, `008900`, `002800`
3. MEDIUM HYBRID: `002600`, `005500`, `009100`, `012400`
4. MEDIUM OCIL: `006200`, `006400`, `007200`, `007300`, `007400`, `009000`, `009200`, `012500`

---

## Notes

- Rules marked **KEEP** still benefit from improved OVAL metadata (title/description fields still contain placeholder text)
- All 35 rules are currently missing `fix:` blocks — remediation scripts should be added after OVAL corrections
- Rules `008500` and `005200` are functionally identical controls; their OVAL checks will be identical
- Rules `008800` and `008900` resolve to the same TLS configuration check; their OVAL will be identical
- Rules `003600` and `004500` resolve to the same authentication mechanisms check
