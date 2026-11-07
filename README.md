# DocGuard

A dependency-free Python documentation checker with a static evidence viewer. Extract explicitly marked Markdown Python examples, validate syntax, optionally run **reviewed trusted** examples, compare stdout, check local file links/anchors, and emit JSON plus GitHub annotation text. An independent portfolio project, not a DataRobot integration.

Live recorded-report viewer: https://docguard-lab.vercel.app

## Reproduce

Python 3.12+; no install step or third-party dependencies.

```sh
python3 -m unittest discover -s tests -v
python3 docguard.py docs --json site/syntax-only.json
python3 docguard.py docs --execute-trusted --json site/passing.json
python3 scripts/build_demo.py
```

`python3 docguard.py fixtures --execute-trusted` must exit 1: the negative-control snippet prints 5 while its expected-output block promises 4. The generated site shows both recorded reports. It is a static viewer: it does NOT execute visitors' code, accept uploads, call an LLM, or connect to a documentation platform.

## Fence format

Pair `python check=example-id` and `text expect=example-id` triple-backtick fences. IDs use lowercase ASCII letters, digits, and hyphens and start with a letter. Each check requires one expected-output block. Normal unmarked code fences are not executed. Expected-output comparison ignores terminal newline differences only. Source SHA-256 fingerprints and file/line locations support investigation; they do not establish content freshness against a product release.

## Scope and safety

**This is not a sandbox.** The default checks syntax without execution. `--execute-trusted` runs code with the current Python interpreter in a temporary working directory with a minimal environment and a timeout. Python `-I`/`-S` do not prevent filesystem or network access. Do not use execution mode on untrusted PRs, user submissions, or arbitrary model outputs. Do not provide secrets. Processes can spawn children and consume resources before timeout; this local runner is deliberately unsuitable for hostile input. Use VM/container isolation with appropriate resource/network controls for untrusted code.

The parser supports a deliberately bounded fence convention, not all CommonMark or MDX. The link checker covers simple local Markdown paths and simple ASCII heading anchors; external links are skipped. It does not run notebooks, inspect screenshots, implement semantic retrieval, invoke Jira/GitHub APIs, or automatically publish documentation. `release_notes()` converts supplied PR-like JSON records into Markdown but does not fetch remote PR data.

## Pull-request checks

`.github/workflows/docs.yml` runs **Documentation quality** on pull requests and pushes to `main`: 22 unit/regression tests, Python compilation, and documentation syntax/local-link validation. Source-line errors appear as GitHub annotations; a JSON report is retained as an artifact for seven days. These are status checks, not mandatory merge protection unless repository branch rules separately require them.

PR events do not execute Markdown snippets. A separate **Reviewed main-branch examples** job runs expected-output comparisons only on `main` pushes or a manually dispatched `main` workflow. It also asserts that the deliberately stale fixture fails with the expected mismatch and exit status, saving both JSON reports. Review code before merging: the local execution helper is not a sandbox.

The workflow uses fresh hosted runners, read-only repository permissions, SHA-pinned actions, no deployment/cloud credentials, five-minute job limits, and cancellation of superseded runs. Checkout credentials are not persisted. Ordinary PR tests still execute repository Python code; do not add secrets or run this on privileged self-hosted runners. Never use `pull_request_target` to execute fork code.

To exercise a failing PR check, temporarily change `docs/quickstart.md` to link to a nonexistent local file. The PR check should fail with `missing_link`; fix the link and push another commit to restore a passing check. Actual run evidence is recorded in `VERIFICATION.md`.

All demo documents, expected outputs, and checks are authored fixtures. No real user adoption, saved engineer-hours, production deployment of the checker, or general documentation coverage is claimed. The public deployment serves recorded evidence only. Code was developed with AI assistance; inspect and understand it before describing your contribution.
