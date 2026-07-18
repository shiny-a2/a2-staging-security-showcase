# Changelog

All notable public showcase updates are documented here. This changelog describes security outcomes without exposing private infrastructure or customer information.

## Unreleased

No changes yet.

## 0.1.2 - 2026-07-18

### Security

- Added a provider-neutral, operator-attested destination-readiness gate before recovery provisioning or capture.
- Bound fresh privacy-filtered readiness evidence to the applicable one-time signed authorization.
- Required conditional creation, bounded independent read-back, exact integrity agreement, narrow cleanup, and one-time evidence consumption.
- Added adversarial coverage for stale, malformed, replayed, cross-scope, replaced, and mismatched readiness evidence.

### Status

- No external storage was provisioned, no provider credentials were handled, and no real destination was probed by this release.
- Provider-neutral software does not automatically prove physical destination independence; that property remains separately attested and reviewed.
- Production backup, restore, staging, and migration remain blocked behind the independent destination, tagged verification, host-readiness, and restore-proof gates.
- The executable staging builder and data sanitizer remain future work.

## 0.1.1 - 2026-07-18

### Security

- Contained one verified legacy sensitive-export exposure with an exact-name HTTP denial while leaving unrelated assets untouched.
- Published the control atomically with exact pre-change binding, metadata preservation, root-only recovery evidence, and idempotent fail-closed behavior.
- Added regression coverage for unsafe links, inherited ACLs, extended attributes, concurrent replacement, incomplete evidence, malformed markers, and accidental payload access.
- Designed the control as monotonic: the tool can add protection but cannot remove it or re-expose the protected artifact.

### Verification

- Confirmed denial at both the public edge and origin without reading the protected payload.
- Confirmed the storefront and product archive remained healthy after containment.
- Required no broad cache purge and made no order, user, checkout, plugin-state, or application-data change.

### Status

- Emergency HTTP containment is active and verified.
- Production backup, restore, staging, and migration remain blocked behind their existing independent gates.
- The executable staging builder and data sanitizer remain future work.

## 0.1.0 - 2026-07-17

### Changed

- Isolated Linux security fixtures from runner-level ACL metadata while preserving mandatory ACL-negative coverage and fail-closed path validation.
- Made encrypted-key fixtures portable across supported OpenSSL versions by generating explicit 16-byte PBKDF2 salts without weakening validation.
- Made isolated MariaDB safety attestation portable across supported runners while preserving strict fail-closed validation.
- Kept MariaDB privilege audits fail-closed while normalizing no-op access metadata and adding an adversarial real-privilege regression fixture.
- Made long-lived MariaDB session markers immediately observable without changing lock, privilege, or timeout policy.
- Made the MariaDB recovery test mirror real read-only backup behavior, avoiding an unnecessary table-lock permission.
- Ensured a failed verified-snapshot capture can never be reported as successful, even inside conditional shell workflows.
- Made abnormal-exit restore quarantine checks deterministic by assigning test lock ownership to one exact process.
- Added a database-enforced release fuse as a third safety layer for the bounded snapshot window, without changing global server policy.
- Bound database encryption and database certificate fingerprints, plus every operational approval check and approval fingerprint, to immutable certificate snapshots so one operation cannot mix trust generations.
- Extended the full security workflow to exact version-tag pushes, tying release evidence to the tagged commit.
- Recorded the bounded-availability authorization while keeping capture blocked behind independent storage, release, signing, and host-readiness gates.
- Strengthened database safety tests to prove lock acquisition and release remain bounded with monotonic timing, without changing global server policy or unrelated sessions.
- Made deliberate process-suspension cleanup bounded and verified that release-tag security jobs cannot be silently skipped.
- Updated an isolated database-contention test to model a real write in progress while leaving all Production code, privileges, and data unchanged.
- Required the public privacy workflow on release tags and added regression coverage against silent gate suppression.

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

- At the time of the `0.1.0` milestone, Production remained unchanged.
- Production capture remains blocked pending an independent off-server destination, fresh signed one-time operating material, and successful host-readiness checks.
- A disposable restore proof from independent read-back remains mandatory after capture.
- The executable staging builder and data sanitizer remain future work.
