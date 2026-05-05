# 1.0.1 - 2026-05-05

## Summary

This patch release increases the allowed range for pytest to include the non-vulnerable 9.0.3.

## Security Issues

This release fixes vulnerabilities by updating dependencies:

| Dependency | Vulnerability | Affected | Fixed in |
|------------|---------------|----------|----------|
| black | CVE-2026-32274 | 25.12.0 | 26.3.1 |
| cryptography | CVE-2026-34073 | 46.0.5 | 46.0.6 |
| cryptography | CVE-2026-39892 | 46.0.5 | 46.0.7 |
| requests | CVE-2026-25645 | 2.32.5 | 2.33.0 |
| pytest | CVE-2025-71176 | 8.4.2 | 9.0.3 |
| tornado | GHSA-78cv-mqj4-43f7 | 6.5.4 | 6.5.5 |
| tornado | CVE-2026-31958 | 6.5.4 | 6.5.5 |
| tornado | CVE-2026-35536 | 6.5.4 | 6.5.5 |
| pyasn1 | CVE-2026-30922 | 0.6.2 | 0.6.3 |
| pygments | CVE-2026-4539 | 2.19.2 | 2.20.0 |

* #19: Fixed vulnerabilities by updated dependencies, increased allowed `pytest` version, and updated to `exasol-toolbox` 7.0.0

## Refactoring

* #9: Removed ignored import `pyexasol` in `pyproject.toml` from `mypy` section, as latest versions are typed

## Dependency Updates

### `main`

* Updated dependency `exasol-saas-api:2.8.0` to `2.10.0`
* Updated dependency `pytest:8.4.2` to `9.0.3`
* Updated dependency `pytest-exasol-backend:1.2.5` to `1.4.1`
* Updated dependency `pytest-exasol-extension:1.0.0` to `1.0.1`

### `dev`

* Updated dependency `exasol-toolbox:5.1.1` to `7.0.0`