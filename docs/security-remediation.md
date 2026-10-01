# Image vulnerability remediation — October 1, 2026

Issue #34 / PR #35 addresses the original SEC-01 baseline. Counts below are package findings, so one CVE affecting several binary packages appears more than once. Both native PR scans gave the same counts.

| Severity | Original Bookworm runtime | Patched Trixie runtime |
| --- | ---: | ---: |
| Critical | 5 | 0 |
| High | 65 | 44 |
| Medium | 120 | 57 |
| Low | 91 | 60 |
| Unknown | 4 | 2 |

The new scans list no findings with a fixed version and no Python package vulnerabilities. This is a point-in-time scan result, not a guarantee that the application has no vulnerabilities. Scanner JSON and image identities are retained in [the PR workflow](https://github.com/kaw393939/is373_ci_cd/actions/runs/36903581374).

## Changes

- Move both stages to digest-pinned Python 3.13.15 on Debian Trixie, with distro updates applied in their shared base stage.
- Remove runtime pip, setuptools, and ensurepip, including pip's unneeded vendored libraries. Keep uv only in the dependency builder.
- Keep UID/GID 10001, root-owned code, read-only filesystem, dropped capabilities, and no-new-privileges. Native container tests additionally verify that runtime installation tools are absent.
- Add no ignore list, database edits, or package-metadata removal to hide findings.

Debian reports Trixie fixes for the original critical [SQLite](https://security-tracker.debian.org/tracker/CVE-2025-7458), [Perl regex](https://security-tracker.debian.org/tracker/CVE-2026-13221), [Perl archive](https://security-tracker.debian.org/tracker/CVE-2026-42496), [Perl overflow](https://security-tracker.debian.org/tracker/CVE-2026-8376), and [zlib](https://security-tracker.debian.org/tracker/source-package/zlib) findings.

## Remaining high findings

There are eight distinct high CVEs across 44 package findings, with no fixed versions in this scan:

- util-linux: CVE-2026-76642, CVE-2026-78408, CVE-2026-78409, CVE-2026-78410 (36 findings across nine packages).
- acl: CVE-2026-54369 (one finding).
- ncurses: CVE-2025-69720 (four findings).
- systemd: CVE-2026-16742 (two findings).
- Perl Archive::Tar: CVE-2026-9538 (one finding, fix deferred).

The current application is a Python HTTP calculator and does not invoke the affected mount, cgroup, home management, or Perl archive operations. That observation is limited to current application code; installed libraries can have other callers. Non-root execution, zero effective capabilities, and no-new-privileges constrain privilege-dependent paths, but findings remain visible until fixed or individually verified as inapplicable.

Continue daily deployed-release rescans and rebuild when patched distro packages/base images become available. Do not force-remove essential Debian packages or silently suppress all unfixed findings to get a green count. A smaller runtime image is a separate compatibility change requiring native build, module/library validation, and deployment tests.
