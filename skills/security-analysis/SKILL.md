---
name: security-analysis
description: The security report format and severity matrix, a source-to-sink method, and the vulnerability categories to cover with their CWE ids. Load when performing a security review, auditing dependencies, or investigating a suspected vulnerability.
---

# Security Analysis

Methodology and report shape for application security assessment.

## Report Format

- `## Security Assessment Summary` - one-paragraph posture and overall risk level.
- `## Attack Surface` - brief trust-boundary and entry-point summary.
- `## Findings` - split by severity using `### CRITICAL`, `### HIGH`,
  `### MEDIUM`, `### LOW`, and `### INFO`. Under each populated subsection, a
  markdown table with columns `Category | Location | Exploitability | Impact |
  Remediation`. Omit empty sections; if there are no findings, say so plainly.
- `## Dependency Audit` - table with columns `Tool | Result | Notes` when
  applicable.
- `## Recommendations` - prioritized remediation plan.
- Keep rows concise. References, exploit-path detail, defense-in-depth notes,
  prevention guidance, or code go in a short `### Detail:` block below the
  relevant table.

### Severity

| Factor | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|
| **Exploitability** | Remote, unauthenticated, trivial | Remote, authenticated or needs specific conditions | Requires local access or social engineering | Requires physical access or insider |
| **Impact** | RCE, full data breach, auth bypass | Significant data access, privilege escalation | Limited data access, single-account takeover | Information disclosure, DoS |
| **Affected users** | All users | Subset of users | Individual user | Admin only |

`INFO` is for defense-in-depth or hardening suggestions that are not an
exploitable vulnerability on their own. Priority follows exploitability and
impact, not theoretical severity. Each finding's remediation is the specific
change for this code, not the generic pattern.

## Method

**Trust boundaries first.** Where does user input enter the system, where does it
talk to external services, where does privilege change, and what runs elevated?
Map entry points (routes, CLI parsing, uploads, sockets, queue consumers,
scheduled jobs) from that.

**Trace sources to sinks.** Sources: request parameters, uploads, database reads
of user-supplied data, external API responses, deserialized data, environment in
shared contexts. Sinks: queries, command execution, file paths, HTML rendering,
server-side HTTP (SSRF), deserialization, crypto, logging, mail and SMS,
redirects. For each path: is the input validated for the target context, is a
parameterized API available and used, and are authorization and rate limits on
the way?

**Cover each category that applies:**

- Injection (CWE-74): SQL, command, template, LDAP/XPath/NoSQL, including ORM raw
  escape hatches.
- Authentication and sessions (CWE-287): hashing algorithm, session invalidation,
  brute-force protection, JWT validation including the `none` algorithm, token
  entropy.
- Access control (CWE-284): every protected endpoint checked server-side, IDOR,
  least privilege, admin role checks, CORS.
- Cryptography (CWE-310): deprecated algorithms, hardcoded keys or IVs, IV reuse,
  CSPRNG, TLS enforcement and certificate validation.
- Sensitive data (CWE-200): hardcoded secrets, `.gitignore` coverage, PII in logs,
  verbose errors, encryption at rest. Find secrets with
  `grep -rEi "password|secret|api.?key|token|private.?key"` and a repeated
  `--include` per extension, since brace expansion does not happen inside quotes.
- Configuration: debug mode, security headers, default credentials, exposed
  debug or admin endpoints, upload restrictions.
- Dependencies: run the ecosystem's audit (`npm audit`, `pnpm audit`,
  `yarn npm audit` on Berry, `pip-audit`, `govulncheck`, `bundle audit`), check
  lock-file pinning, and look for abandoned packages and typosquats.

**For larger assessments, threat-model with STRIDE:** spoofing, tampering,
repudiation, information disclosure, denial of service, elevation of privilege.
One question each: can an attacker do it?

Never inspect `.env`, credential files, private keys, or similar secret-bearing
files, including through `git diff` or `git show`.
