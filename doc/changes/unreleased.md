# Unreleased

## Summary

This patch release increases the allowed range for pytest to include the non-vulnerable 9.0.3.

## Security Issues

* #19: Fixed vulnerabilities by updated dependencies, increased allowed `pytest` version, and updated to `exasol-toolbox` 7.0.0

## Refactoring

* #9: Removed ignored import `pyexasol` in `pyproject.toml` from `mypy` section, as latest versions are typed