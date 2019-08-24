import inspect
import traceback
import code
import sys
from io import StringIO

def get_call_stack():
    frame = inspect.currentframe()
    # Skip this function and caller
    frame = frame.f_back
    frame = frame.f_back

    # Build a list of the locals in each caller in the stack
    stack = []
    while frame is not None:
        vars = dict(frame.f_globals, **frame.f_locals)
        stack.append(vars)
        frame = frame.f_back
    return stack


def let_me_try(f):
    def wrapper(*args, **kwargs):
        run_again = True
        _ret_val = None
        while run_again:
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print('Caught exception:', e)
                traceback.print_exc()
                orig_stdin = sys.stdin
                empty_stdin = StringIO('')

                def resume(*new_args, **new_kwargs):
                    nonlocal args, kwargs
                    sys.stdin = empty_stdin
                    args = new_args
                    kwargs = new_kwargs
                    print("Trying call to {} again with new arguments".format(f.__name__))

                def skip(ret_val=None):
                    nonlocal run_again, _ret_val
                    # Set return value for once the console exits
                    _ret_val = ret_val
                    # Stop the retry loop
                    run_again = False
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
                if f.__name__.isidentifier():
                    locals[f.__name__] = resume

                code.interact('Call to {} failed, dropping to console'.format(f.__name__),
                              local=locals,
                              exitmsg='Resuming execution')
                if sys.stdin is empty_stdin:
                    sys.stdin = orig_stdin
        # Return the value passed to skip instead of a result from f
        return _ret_val
    return wrapper


def try_again(f):
    pass


