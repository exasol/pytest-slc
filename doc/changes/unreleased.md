# Unreleased

## Summary

This release adds a meaningful exception message when `wait_for_messages()` and convenience function `pyexasol_query_func()` and updates the user guide to describe class `UdfOutputLogger` and these functions.

## Bugfixes

* #45: Added exception message in case of expected message not found in `wait_for_messages()`

## Documentation

* #46: Described `UdfOutputLogger` and `wait_for_messages()` in the user guide

## Refactorings

* #43: Replaced CLI option `--db-version` by `--itde-db-version`
