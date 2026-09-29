# Complementary-hosting validation record

This extension is tracked in [issue #28](https://github.com/kaw393939/is373_ci_cd/issues/28). The related release-selection defect is tracked in [issue #25](https://github.com/kaw393939/is373_ci_cd/issues/25).

## Checks performed during implementation

- Local unit checks: 34 passed, including rejection of wrong-platform/rebuilt artifacts, preservation of the local Compose override, persisted release precedence, and refusal of a mismatched container image ID.
- Local FastAPI integration checks: 16 passed. Existing dependency deprecation warnings remain; no application HTTP behavior changed.
- The pinned Python and WUD registry indexes were inspected and contain both linux/amd64 and linux/arm64 manifests.
- New CI jobs perform native browser tests on both architectures; their actual results and image/test evidence are attached to the [workflow runs](https://github.com/kaw393939/is373_ci_cd/actions/workflows/ci.yml). The stable `verify` result requires both jobs.
- The main-only publication job records the multi-platform index and child digests in its summary and artifact. This is separate from PR verification.

## Explicit limits

The extension does not change the running classroom VPS or the original local Docker demonstration. No new public calculator deployment, WUD network-preservation rehearsal, or remote rollback/resume is claimed by these repository edits. The companion's final lab specifies the observations needed to prove those behaviors.

The release-selection regression is tested without changing live production. Issue #25's requested full operational rollback rehearsal remains distinct from the code fix and should be recorded when performed. Existing historical ARM64 evidence remains in [evidence.md](evidence.md).
