.. _user_guide:

:octicon:`person` User Guide
============================


UDF Output Logger
-----------------
.. _script_output: https://docs.exasol.com/db/latest/database_concepts/udf_scripts/debug_udf_script_output.htm

The Pytest SLC Plugin helps accessing and analyzing the output of UDFs (User
Defined Functions), see `docs.exasol.com <script_output_>`_.

Since UDFs cannot print to your console, you only can retrieve messages from
UDFs via network transfer, e.g. using *sockets*. PYTSLC class
``UdfOutputLogger`` can redirect output from UDFs to your local console or
wait for specific messages.

The class can be used as a context with the following arguments:

.. list-table::
   :header-rows: 1
   :widths: 10 30

   * - Argument
     - Default value and alternatives
   * - ``query`` (mandatory)
     - ``pyexasol_query_func(pyexasol_connection)``
   * - ``host`` (optional)
     - Default: ``localhost`` as seen from a UDF,
       even when ``dockerd`` runs in a virtual machine
   * - ``print_func`` (optional)
     - Default: ``print``, alternatively use ``LogPipe``

The following minimal example uses ``pyexasol_query_func()`` and prints the
UDF output to stdout.

.. code-block:: python
    :caption: Minimal Example

    from exasol.pytest_slc import udf_debug as ud

    query = ud.pyexasol_query_func(pyexasol_connection)
    with ud.UdfOutputLogger(query):
        query("SELECT print_something() FROM DUAL")


Here is an example, using a ``LogPipe`` and waiting for a specific message.

.. code-block:: python
    :caption: Example using ``LogPipe``

    from exasol.pytest_slc import udf_debug as ud

    query = ud.pyexasol_query_func(pyexasol_connection)
    pipe = ud.LogPipe()
    with ud.UdfOutputLogger(query, print_func=pipe.input):
        query("SELECT print_something() FROM DUAL")
        ud.wait_for_messages(pipe.output, "Hello from UDF")

Function ``wait_for_messages()`` has the following arguments:

.. list-table::
   :header-rows: 1
   :widths: 10 30

   * - Argument
     - Default value and alternatives
   * - ``read_line`` (mandatory)
     - Function to retrieve new messages, use ``LogPipe.output`` for example.
   * - ``*expected_messages`` (mandatory)
     - One or multiple messages of type ``str`` to wait for.
   * - ``timeout`` (optional)
     - Default: 10 seconds.
