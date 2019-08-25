from unittest import TestCase
from plsnocrash import retry
from .common import StdIOMonkeyPatch

SIG_STR = "AAAAAAAAAA"


class TestRetry(TestCase):
    def test_id(self):
        @retry
        def id(x):
            return x
        self.assertEqual('test', id('test'))

    def test_fail1(self):
        @retry
        def fail1():
            print(SIG_STR)
            raise ValueError()
        streams = StdIOMonkeyPatch()
        with streams:
            try:
                fail1()
            except ValueError as e:
                # Expected error
                pass
            else:
                self.fail('Did not reraise exception')
        out = streams.get_stdout()
        self.assertEqual(out.count(SIG_STR), 2)

    def test_fail5(self):
        @retry(5)
        def fail5():
            print(SIG_STR)
            raise ValueError()
        streams = StdIOMonkeyPatch()
        with streams:
            try:
                fail5()
            except ValueError as e:
                # Expected error
                pass
            else:
                self.fail('Did not reraise exception')
        out = streams.get_stdout()
        self.assertEqual(out.count(SIG_STR), 6)

    def test_fail_then_succeed(self):
        @retry(limit=None)
        def fail_then_succeed(ct_ref, limit):
            print(SIG_STR)
            # Fail until count in ct_ref is equal to limit
            if ct_ref[0] < limit:
                ct_ref[0] += 1
                raise ValueError()

        streams = StdIOMonkeyPatch()
        with streams:
            fail_then_succeed([0], 10)
        out = streams.get_stdout()
        self.assertEqual(out.count(SIG_STR), 11)

    def test_invalid_limit(self):
        self.assertRaises(ValueError, lambda: retry(-1)(lambda: 1/0))
        self.assertRaises(ValueError, lambda: retry(-400)(lambda: 1/0))
        self.assertRaises(ValueError, lambda: retry('None')(lambda: 1/0))



