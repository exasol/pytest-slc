# 1.2.0 - 2026-08-25

## Summary

This release adds a meaningful exception message for `wait_for_messages()`, a new convenience function `pyexasol_query_func()` and updates the user guide to describe class `UdfOutputLogger` and these functions.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| cryptography | PYSEC-2026-3552 | 49.0.0 | 50.0.0 |
| gitpython | GHSA-2f96-g7mh-g2hx | 3.1.50 | 3.1.51 |
| gitpython | GHSA-v396-v7q4-x2qj | 3.1.50 | 3.1.51 |
| gitpython | GHSA-956x-8gvw-wg5v | 3.1.50 | 3.1.51 |
| gitpython | GHSA-3rp5-jjmw-4wv2 | 3.1.50 | 3.1.53 |
| gitpython | GHSA-fjr4-x663-mwxc | 3.1.50 | 3.1.54 |
| gitpython | GHSA-6p8h-3wgx-97gf | 3.1.50 | 3.1.54 |
| gitpython | GHSA-r9mr-m37c-5fr3 | 3.1.50 | 3.1.54 |
| gitpython | GHSA-94p4-4cq8-9g67 | 3.1.50 | 3.1.55 |
| gitpython | CVE-2026-73620 | 3.1.50 | 3.1.57 |
| gitpython | GHSA-p538-c434-8v24 | 3.1.50 | 3.1.56 |
| gitpython | GHSA-9rj7-rf2p-w77r | 3.1.50 | 3.1.58 |
| gitpython | GHSA-4gmw-gg2m-w46p | 3.1.50 | 3.1.58 |
| gitpython | CVE-2026-76217 | 3.1.50 | 3.1.58 |
| gitpython | GHSA-wvpp-8hx9-p66j | 3.1.50 | 3.1.58 |
| gitpython | GHSA-jm78-9fvv-mhgr | 3.1.50 | 3.1.58 |
| pip | PYSEC-2026-3721 | 26.1.2 | 26.2 |

## Features

* #47: Added convenience function `pyexasol_query_func()`
* #25: Added commandline option --script-languages
* 

## Bugfixes

* #45: Added exception message in case of expected message not found in `wait_for_messages()`

## Documentation

* #46: Described `UdfOutputLogger` and `wait_for_messages()` in the user guide
* #27: Described deploying and activating an SLC via Integration tests in the User guide

## Refactorings

* #43: Replaced CLI option `--db-version` by `--itde-db-version`
*  #4: Added support for Python 3.14

## Dependency Updates

### `main`

* Updated dependency `exasol-python-extension-common:0.16.0` to `1.0.0`
* Added dependency `pyexasol:2.3.1`
* Updated dependency `pytest-exasol-backend:1.5.0` to `1.5.1`
* Updated dependency `pytest-exasol-extension:1.0.1` to `1.1.0`

### `dev`

* Updated dependency `exasol-bucketfs:2.2.0` to `2.3.0`
* Updated dependency `exasol-toolbox:10.2.1` to `10.4.0`
