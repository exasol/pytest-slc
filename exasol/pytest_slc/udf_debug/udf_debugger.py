"""
Support for capturing the output of UDFs.
"""

from exasol.pytest_slc.udf_debug.script_output_redirect import (
    PrintFunc,
    QueryFunc,
    ScriptOutputRedirect,
)


class UdfDebugger:
    """
    Context manager for temporary UDF output redirection.
    """

    def __init__(
        self,
        query: QueryFunc,
        server: str | None = None,
        print_func: PrintFunc | None = None,
    ):
        self._redirect = ScriptOutputRedirect(
            query=query,
            host=server,
            print_func=print_func,
        )

    def __enter__(self):
        return self.start()

    def __exit__(self, type_, value, trace_back):
        self._redirect.disable()

    def start(self):
        """
        Explicitly enter the debugger context.
        """
        self._redirect.activate()
        return self

    def stop(self, type_=None, value=None, trace_back=None):
        """
        Explicitly exit the debugger context.
        """
        return self.__exit__(type_, value, trace_back)
