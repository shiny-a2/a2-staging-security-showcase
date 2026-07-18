# Security Policy

## Public repository boundary

This repository is a sanitized showcase. It does not contain deployable production code, operational credentials, customer data, backup artifacts, private topology, or infrastructure-specific configuration.

The descriptions here are intentionally outcome-oriented. Detailed operating procedures, trust material, internal paths, authorization records, and recovery evidence remain in controlled private systems.

## Design principles represented

- Fail closed when authorization, artifact integrity, environment isolation, or evidence is incomplete.
- Encrypt backup data while streaming and avoid persistent plaintext intermediates.
- Separate signing purposes and scope approvals to a single intended operation.
- Bind fresh, privacy-filtered destination-readiness evidence to applicable one-time approvals before high-impact recovery work can begin.
- Require conditional probe creation, bounded read-back, narrow cleanup, and fail-closed replay handling without publishing provider details.
- Validate restores in a disposable isolated environment before considering a backup usable.
- Preserve auditable evidence without exposing secrets or personal information.
- Quarantine ambiguous database or recovery state until independent clearance is proven.
- Bind destructive cleanup to an exact disposable process identity rather than a mutable socket or PID-file path.
- Keep production changes narrowly scoped, explicitly authorized, independently verified, and fail closed when prerequisites are incomplete.
- Prefer monotonic emergency controls that cannot silently restore a proven exposure.

## Reporting a security concern

Please report suspected vulnerabilities privately to the repository owner. Do not open a public issue containing exploit details, credentials, personal data, customer information, or infrastructure identifiers.

Include only the minimum information needed to reproduce the concern safely. Public disclosure should wait until the issue has been assessed and a coordinated remediation plan is available.

## Supported version

The current documented showcase version is `0.1.2`.
