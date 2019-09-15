from __future__ import print_function
import inspect
import keyword
import string
import traceback
import code
import sys
# Python 2 compat, StringIO moved
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


# Python 2 compat, no isidentifier method
try:
    isidentifier = str.isidentifier
except AttributeError:
    def isidentifier(ident):
        """Determines if string is valid Python identifier."""

        if not isinstance(ident, str):
            raise TypeError("expected str, but got {!r}".format(type(ident)))

        if not ident:
            return False

        if keyword.iskeyword(ident):
            return False

        first = '_' + string.lowercase + string.uppercase
        if ident[0] not in first:
            return False

        other = first + string.digits
        for ch in ident[1:]:
            if ch not in other:
                return False

        return True


def get_call_stack():
    frame = inspect.currentframe()
    # Skip this function
    frame = frame.f_back
    # Skip the function that called this function
    frame = frame.f_back

    # Build a list of the locals in each caller in the stack above/before the wrapper
    stack = []
    while frame is not None:
        vars = dict(frame.f_globals, **frame.f_locals)
        stack.append(vars)
        frame = frame.f_back

    # Get the vars for the calls below/after the wrapper
    trace = inspect.trace()[1:]
    stack = [dict(frame[0].f_locals, **frame[0].f_globals) for frame in reversed(trace)] + stack
    return stack


def build_letmetry_helptext(fname, args, kwargs):
    if isidentifier(fname):
        resume_str = "{}(arg1, ...) or ".format(fname)
    else:
        resume_str = ''
    f_str = "Call to {0}(args={1}, kwargs={2}) failed.\n\n" \
        "Use {3}resume(arg1, ...) to call the function again with the given arguments and resume execution.\n" \
        "If the function raises another exception, you will end up at another console.\n\n" \
        "Use skip(return_value) to skip the function call and resume execution as if it had " \
            "returned 'return_value'.\n\n" \
        "Global and local variables are available for all scopes on the call stack under the list call_stack. \n" \
        "e.g. call_stack[0]['x'] returns the variable 'x' from {0} (the failing function), \nand call_stack[1]['y'] " \
        "returns the variable 'y' from the function that called {0}.\n\n" \
        "The original positional arguments are available as the tuple 'args', \n" \
        "and keyword arguments are available as the dictionary 'kwargs'.\n\n" \
        "Use quit() or exit() to give up and stop the whole program."
    return f_str.format(fname, str(args), str(kwargs), resume_str)


def let_me_try(f):
    """
    Decorator that drops to an interactive interpreter if the wrapped function raises an exception. The interpreter
    has access to all of the local variables available in the wrapped function when it crashed, as well as the variables
    from all other functions on the call stack. You can use this interpreter to fix whatever went wrong with the
    function and then resume execution, or you can skip the function all together with some simulated return value.

    Example:

    ::

        root@710027b06106:/plsnocrash/examples# cat let_me_try.py
        import plsnocrash

        import time
        import pickle

        def train():
            time.sleep(10)
            return [1,2,3,4,5]

        @plsnocrash.let_me_try
        def save(x):
            # Oops, that should be a file object, not a string
            pickle.dump(x, 'test.pkl')

        if __name__ == '__main__':
            x = train()
            save(x)
            print("All done!")
        root@710027b06106:/plsnocrash/examples# python let_me_try.py
        Caught exception: file must have a 'write' attribute
        Traceback (most recent call last):
          File "/usr/local/lib/python3.7/site-packages/plsnocrash/plsnocrash.py", line 65, in wrapper
            return f(*args, **kwargs)
          File "let_me_try.py", line 13, in save
            pickle.dump(x, 'test.pkl')
        TypeError: file must have a 'write' attribute
        Call to save(args=([1, 2, 3, 4, 5],), kwargs={}) failed.

        ...
        [Some help text]
        ...

        >>> import pickle
        >>> pickle.dump(args[0], open('test.pkl','wb'))
        >>> skip()
        Call skipped
        >>>
        Resuming execution
        All done!
        root@710027b06106:/plsnocrash/examples# ls
        test.pkl


    :param f: Function to wrap
    :return: Wrapped function
    """
    def wrapper(*args, **kwargs):
        # Use this dictionary instead of the 'nonlocal' keyword to modify things in closures for python27 compatibility
        nonlocal_dict = {'run_again': True, 'ret_val': None, 'args': args, 'kwargs': kwargs}
        while nonlocal_dict['run_again']:
            try:
                return f(*nonlocal_dict['args'], **nonlocal_dict['kwargs'])
            except Exception as e:
                print('Caught exception:', e)
                traceback.print_exc()
                orig_stdin = sys.stdin
                empty_stdin = StringIO('')

                def resume(*new_args, **new_kwargs):
                    sys.stdin = empty_stdin
                    nonlocal_dict['args'] = new_args
                    nonlocal_dict['kwargs'] = new_kwargs
                    print("Trying call to {} again with new arguments".format(f.__name__))

                def skip(ret_val=None):
                    # Set return value for once the console exits
                    nonlocal_dict['ret_val'] = ret_val
                    # Stop the retry loop
                    nonlocal_dict['run_again'] = False
                    # Exit the console
                    sys.stdin = empty_stdin
                    print("Call skipped")

                call_stack = get_call_stack()
                locals = {
                    'args': args,
                    'kwargs': kwargs,
                    'skip': skip,
                    'resume': resume,
                    'call_stack': call_stack,
                }
                # Add the original name of f as an alias for resume, if it is a valid identifier (e.g. not <lambda>)
                if isidentifier(f.__name__):
                    locals[f.__name__] = resume

                code.interact(banner=build_letmetry_helptext(f.__name__, args, kwargs),
                              local=locals)
                if sys.stdin is empty_stdin:
                    sys.stdin = orig_stdin
        # Return the value passed to skip instead of a result from f
        return nonlocal_dict['ret_val']

    return wrapper


def retry(limit=1):
    """
    Retry a failing function `n` times or until it executes successfully. If the function does not complete
    successfully by the nth retry, then the exception will be reraised for the executing code to handle.

    Example:

    ::

        root@710027b06106:/plsnocrash/examples# cat retry.py
        import plsnocrash

        fail_counter = 0

        @plsnocrash.retry(5)
        def get_data():
            global fail_counter
            # Fail three times before completing
            if fail_counter < 3:
                fail_counter += 1
                raise ValueError("Something went wrong")
            return "some data"


        if __name__ == '__main__':
            print(get_data())
        root@710027b06106:/plsnocrash/examples# python retry.py
        Caught exception: Something went wrong, retry 1/5
        Caught exception: Something went wrong, retry 2/5
        Caught exception: Something went wrong, retry 3/5
        some data


    :param f: Function to wrap
    :param limit: int, number of retries. If None then retry forever. Default 1.
    :type limit: int
    :return: Wrapped function
    """

    # Implementation notes:
    # Three ways this could be called as a decorator:
    # @retry -- Gets used as a raw decorator, limit is actually a function, this is handled below
    # @retry() -- default value on limit actually gets used, limit is set to 1
    # @retry(value) or @retry(limit=value) -- value is assigned to limit

    def retry_decorator(f):
        if not (limit is None or (isinstance(limit, int) and limit >= 0)):
            raise ValueError('Invalid repeat limit', limit)
        if limit is None:
            def inf_wrapper(*args, **kwargs):
                i = 1
                while True:
                    try:
                        return f(*args, **kwargs)
                    except Exception as e:
                        print("Caught exception {}, retry {:d}/inf".format(e, i))
                        i += 1
                        continue
            return inf_wrapper
        else:
            def wrapper(*args, **kwargs):
                for i in range(limit+1):
                    try:
                        return f(*args, **kwargs)
                    except Exception as e:
                        print("Caught exception: {}, retry {:d}/{:d}".format(e, i+1, limit))
                        # Reraise exception if does not succeed by final retry
                        if i == limit:
                            raise e

            return wrapper
    # if used as a decorator without an argument, default to 1
    if callable(limit):
        f = limit
        limit = 1
        return retry_decorator(f)
    return retry_decorator

