Manual Experiments with an SLC
==============================

.. _pytbe_readme:
   https://github.com/exasol/pytest-backend#re-using-an-external-or-local-database
.. _pytext_pyexasol_con:
   https://github.com/exasol/pytest-extension/blob/main/exasol/pytest_extension/__init__.py#L56

For manual Experiments with an SLC we recommend simply using the fixtures from
this pytest plugin ``pytest-exasol-slc`` for deploying and activating the SLC.

For this usage scenario

* Start a Docker DB manually and tell pytest plugin ``pytest-exasol-backend``
  to use it, see `PYTBE README <pytbe_readme_>`_.
* The integration tests in your project will use pytest plugin ``pytest-slc``
  for deploying and activating your SLC.
* As ``pytest-slc`` usually activates the SLC on ``SYSTEM`` level and also
  doesn't remove the uploaded SLC after pytest has terminated, you easily can
  use the language alias interactively in an SQL Editor.

Additionally, you can also **keep the database schema** created by pytest
plugin ``pytest-extension``:

Normally ``pytest-extension`` deletes the DB schema after pytest has
terminated, but not if you **create the DB schema before running the
integration tests**, see fixture `pyexasol_connection
<pytext_pyexasol_con_>`_.

