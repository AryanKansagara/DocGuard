# Verification on November 7 2026

- 22 Python unittest cases passed, including syntax, parsing, expected-output mismatches, execution failure, timeout, output size, link boundaries, annotation escaping, and deterministic release-summary conversion.
- Two reviewed quickstart examples executed locally and matched stdout. The separate stale-output fixture produced one failure and a nonzero checker exit status.
- The generated JSON reports were deployed as static files to the Vercel Hobby project `aryankansagaras-projects/docguard-lab`.
- Public HTTP checks returned 200 for the viewer and both report files.
- Browser check: initial report showed two passes; selecting the stale-example control displayed one failure, source `drift.md:5`, expected `4`, and actual `5`.

## Active GitHub Actions verification

- Enabled `.github/workflows/docs.yml` for pull requests, main pushes, and manual dispatch. Actionlint 1.7.12 passed locally; downloaded binary checksum verified against its release checksum file.
- [Initial main run](https://github.com/AryanKansagara/DocGuard/actions/runs/42409365993) passed both jobs: 22 tests, compilation, syntax/link validation, two executed quickstart examples, and the stale-output negative control. JSON artifacts were uploaded successfully.
- [PR #1](https://github.com/AryanKansagara/DocGuard/pull/1) deliberately linked to a missing guide. Its [first run](https://github.com/AryanKansagara/DocGuard/actions/runs/42409393832) failed at documentation validation with `missing_link` and exit 1.
- Added the guide on the same branch; the [replacement PR run](https://github.com/AryanKansagara/DocGuard/actions/runs/42409455798) passed. Markdown execution was skipped on PR events as designed.
- These checks are active status checks; branch protection is not configured and mandatory merge enforcement is not claimed. Permissions are read-only, actions SHA-pinned, no cloud/deployment secrets supplied, and checkout credentials not persisted.

Only authored synthetic fixtures were used. The static deployment does not run code or provide an API. The checker was not deployed as a service. No live LLM calls, notebook execution, Jira integration, or third-party documentation defects are claimed.
