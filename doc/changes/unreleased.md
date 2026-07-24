# Unreleased

## Summary

This release adds a meaningful exception message for `wait_for_messages()`, a new convenience function `pyexasol_query_func()` and updates the user guide to describe class `UdfOutputLogger` and these functions.

## Features

* #47: Added convenience function `pyexasol_query_func()`

## Bugfixes

* #45: Added exception message in case of expected message not found in `wait_for_messages()`

## Documentation

* #46: Described `UdfOutputLogger` and `wait_for_messages()` in the user guide
* #27: Described deploying and activating an SLC via Integration tests in the User guide

## Refactorings

* #43: Replaced CLI option `--db-version` by `--itde-db-version`

## Features

* #25: Added commandline option --script-languages
