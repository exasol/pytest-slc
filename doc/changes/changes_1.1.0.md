# 1.1.0 - 2026-07-06

## Summary

This release moves class `UdfDebugger` from [exasol-python-test-framework](https://github.com/exasol/exasol-python-test-framework) to PYTSLC class `UdfOutputLogger`.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| cryptography | GHSA-537c-gmf6-5ccf | 48.0.0 | 48.0.1 |
| gitpython | GHSA-mv93-w799-cj2w | 3.1.49 | 3.1.50 |
| idna | PYSEC-2026-215 | 3.11 | 3.15 |
| msgpack | GHSA-6v7p-g79w-8964 | 1.1.2 | 1.2.1 |
| pip | PYSEC-2026-196 | 26.1.1 | 26.1.2 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| starlette | PYSEC-2026-161 | 0.52.1 | 1.0.1 |
| starlette | PYSEC-2026-249 | 0.52.1 | 1.3.1 |
| starlette | PYSEC-2026-248 | 0.52.1 | 1.3.0 |
| starlette | CVE-2026-48818 | 0.52.1 | 1.1.0 |
| starlette | CVE-2026-48817 | 0.52.1 | 1.1.0 |
| tornado | CVE-2026-49854 | 6.5.5 | 6.5.6 |
| tornado | CVE-2026-49853 | 6.5.5 | 6.5.6 |
| tornado | CVE-2026-49855 | 6.5.5 | 6.5.6 |
| tornado | GHSA-pw6j-qg29-8w7f | 6.5.5 | 6.5.7 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-142 | 2.6.3 | 2.7.0 |
| urllib3 | PYSEC-2026-141 | 2.6.3 | 2.7.0 |

## Features

* #36: Added functions to wait for a list of messages in a io.TextIO or file

## Refactoring

* #22: Updated `exasol-toolbox` to 8.1.1
* #32: Updated `exasol-toolbox` to 10.0.0
* #26: Moved UdfDebugger from exasol-python-test-framework
* #38: Added integration test for `UdfOutputLogger`

## Dependency Updates

### `main`

* Updated dependency `exasol-python-extension-common:0.12.1` to `0.16.0`
* Updated dependency `pytest:9.0.3` to `9.1.1`
* Updated dependency `pytest-exasol-backend:1.4.1` to `1.5.0`

### `dev`

* Updated dependency `exasol-bucketfs:2.1.0` to `2.2.0`
* Updated dependency `exasol-toolbox:7.0.0` to `10.1.0`