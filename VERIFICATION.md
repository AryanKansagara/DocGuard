# Verification on November 7 2026

- 22 Python unittest cases passed, including syntax, parsing, expected-output mismatches, execution failure, timeout, output size, link boundaries, annotation escaping, and deterministic release-summary conversion.
- Two reviewed quickstart examples executed locally and matched stdout. The separate stale-output fixture produced one failure and a nonzero checker exit status.
- The generated JSON reports were deployed as static files to the Vercel Hobby project `aryankansagaras-projects/docguard-lab`.
- Public HTTP checks returned 200 for the viewer and both report files.
- Browser check: initial report showed two passes; selecting the stale-example control displayed one failure, source `drift.md:5`, expected `4`, and actual `5`.

Only authored synthetic fixtures were used. The static deployment does not run code or provide an API. The checker was not deployed as a service. No live LLM calls, notebook execution, Jira integration, or enabled remote GitHub Actions run was performed. The workflow file is an inactive example.
