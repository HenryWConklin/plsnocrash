from unittest import TestCase
from plsnocrash import let_me_try
from .common import StdIOMonkeyPatch

@let_me_try
def wrapped_id(x):
    return x

@let_me_try
def wrapped_crash(x):
    if x is True:
        raise ValueError('An error')
    return x

GLOBAL_VAR = 'BBBBBBBBBBBB'

class TestLet_me_try(TestCase):
    def test_no_error(self):
        x = 'a string'
        self.assertEqual(x, wrapped_id(x))

    def test_catch_crash(self):
        # Pass 'quit()' to stdin to kill the console
        streams = StdIOMonkeyPatch('skip()\n')
        with streams:
            wrapped_crash(True)

        # Did not crash, automatic pass

    def test_resume(self):
        streams = StdIOMonkeyPatch('resume(False)\n')
        with streams:
            wrapped_crash(True)
        # Test calling resume with original function name
        streams = StdIOMonkeyPatch('wrapped_crash(False)\n')
        with streams:
            wrapped_crash(True)

    def test_skip(self):
        streams = StdIOMonkeyPatch('skip()\n')
        with streams:
            wrapped_crash(True)

    def test_console_opened(self):
        # Try to exec 5+5 to verify that a console actually opened
        streams = StdIOMonkeyPatch('5 + 5\nskip()\n')
        with streams:
            wrapped_crash(True)
        out = streams.get_stdout()
        self.assertIn('10\n', out)

    def test_args_available(self):
        streams = StdIOMonkeyPatch('args\nskip()\n')
        with streams:
            wrapped_crash(True)
        out = streams.get_stdout()
        self.assertIn('(True,)\n', out)

    def test_kwargs_available(self):
        streams = StdIOMonkeyPatch('kwargs\nskip()\n')
        with streams:
            wrapped_crash(x=True)
        out = streams.get_stdout()
        self.assertIn("{'x': True}\n", out)

    def test_catch_arg_error(self):
        streams = StdIOMonkeyPatch('skip()\n')
        with streams:
            # Call with no arguments, expects 1 argument
            wrapped_crash()
        # No crash, passed

    def test_callstack_vars(self):
        grab_me = "AAAAAAA"
        streams = StdIOMonkeyPatch("call_stack[0]['x']\n"
                                   "call_stack[1]['grab_me']\n"
                                   "call_stack[1]['GLOBAL_VAR']\n"
                                   "skip()\n")
        with streams:
            wrapped_crash(True)
        out = streams.get_stdout()
        self.assertIn(grab_me, out)
        self.assertIn(GLOBAL_VAR, out)
        self.assertIn('True', out)

    def test_skip_returnval(self):
        streams = StdIOMonkeyPatch('skip(123)\n')
        with streams:
            retval = wrapped_crash(True)
        self.assertEqual(retval, 123)



