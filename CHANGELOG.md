# Changelog

All notable public showcase updates are documented here. This changelog describes security outcomes without exposing private infrastructure or customer information.

## Unreleased

### Changed

- Isolated Linux security fixtures from runner-level ACL metadata while preserving mandatory ACL-negative coverage and fail-closed path validation.
- Made encrypted-key fixtures portable across supported OpenSSL versions by generating explicit 16-byte PBKDF2 salts without weakening validation.
- Made isolated MariaDB safety attestation portable across supported runners while preserving strict fail-closed validation.
- Kept MariaDB privilege audits fail-closed while normalizing no-op access metadata and adding an adversarial real-privilege regression fixture.

## 0.1.0 - 2026-07-14

### Added

- Encrypted streaming backup orchestration for mixed database engine workloads.
- Fail-closed validation of signed inventory, purpose-separated signatures, and one-time approvals.
- Recoverable finalization state, a signed artifact index, and privacy-safe audit evidence.
- Disposable isolated restore-verification workflow.
- Durable fail-closed quarantine for unproven temporary database-session cleanup.
- Exact process-identity cleanup, signal-safe worker guards, and fresh lock-generation proof before raw-data deletion.
- Redundant capture-deadline supervision with independently verified release evidence.
- Authentication-before-parsing of approval and recovery metadata.
- Rejection of inherited, indirect, and delegable backup permissions.
- Independent early cleanup of validated short-lived decryption material.
- A public privacy gate for credentials, private topology, sensitive artifacts, and Git metadata.
- Automated tests and continuous-integration checks for workflow contracts, cryptographic policy, failure paths, and sensitive-content hygiene.
- Publicly documented boundary between the implemented recovery foundation and the staging isolation/sanitization design contract.

### Status

- Production remains unchanged.
- Production execution remains blocked pending an independent off-server destination, successful restore proof, and explicit availability approval.
- The executable staging builder and data sanitizer remain future work.
