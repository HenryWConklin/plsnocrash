from io import StringIO
import sys


class StdIOMonkeyPatch:
    """
    Intercept stdin, stdout, and stderr so tests can read
    what was printed and simulate console input
    """
    def __init__(self, stdin=None):
        """
        Intercept stdin, stdout, and stderr so tests can read what was printed and simulate console input.
        stdout and stderr will be extended with new data rather than overwritten if this object is used multiple
        times. stdin will receive any unused text from the last 'with' block if this object is used in multiple 'with'
        blocks

        usage:

        ::

            streams = StdIOMonkeyPatch("input text")
            with streams:
                print("something")
                print("an error", file=sys.stderr)
            print("outside the block") # prints to console, or goes to wherever stdin was originally pointed
            stdout_text = streams.get_stdout() # gives the string "something\\n"
            stderr_text = streams.get_stderr() # gives the string "an error\\n"

        :param stdin: String, text to feed to stdin as if it were entered on the console, if None stdin is left alone. Default None
        :type stdin: str
        """
        if stdin is not None:
            self.stdin_buff = StringIO(stdin)
        else:
            self.stdin_buff = None
        self.stdout_buff = StringIO()
        self.stderr_buff = StringIO()

    def get_stderr(self):
        return self.stderr_buff.getvalue()

    def get_stdout(self):
        return self.stdout_buff.getvalue()

    def __enter__(self):
        self.orig_stdin = sys.stdin
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

        if self.stdin_buff is not None:
            sys.stdin = self.stdin_buff

        sys.stdout = self.stdout_buff
        sys.stderr = self.stderr_buff

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdin = self.orig_stdin
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr

