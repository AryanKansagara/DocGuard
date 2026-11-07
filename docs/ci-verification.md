# CI verification guide

Every pull request runs unit tests, Python compilation, and syntax/local-link checks.
The checker emits source-line annotations and saves a JSON report as an artifact.

## Reproduce a regression

1. Add a Markdown link to a nonexistent file in a documentation page.
2. Push the change on a branch and open a pull request.
3. Confirm **Documentation quality** fails with `missing_link`.
4. Add the missing page or correct the target, then push again.
5. Confirm the replacement check passes; inspect its JSON report artifact.

[Back to quickstart](quickstart.md)

## Execution boundaries

PR checks do not execute Markdown examples. Unit tests execute repository code on
an ephemeral GitHub-hosted runner, without cloud/deployment secrets. Reviewed
main-branch examples run in a separate job after a main push or manual main run.
The runner is not a security sandbox and must not receive unreviewed snippets.
Status checks are visible on PRs but are not mandatory merge protection by default.
