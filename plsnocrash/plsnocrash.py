import traceback
import code
import sys
from io import StringIO


def let_me_try(f):
    def wrapper(*args, **kwargs):
        run_again = True
        while run_again:
            try:
                return f(*args, **kwargs)
            except Exception as e:
                print('Caught exception:', e)
                orig_stdin = sys.stdin
                empty_stdin = StringIO('')

                def resume(*new_args, **new_kwargs):
                    nonlocal args, kwargs
                    sys.stdin = empty_stdin
                    args = new_args
                    kwargs = new_kwargs
                    print("Trying call to {} again with new arguments".format(f.__name__))

                def skip():
                    nonlocal run_again
                    run_again = False
                    sys.stdin = empty_stdin
                    print("Call skipped")

                locals = {
                    'args': args,
                    'kwargs': kwargs,
                    'skip': skip,
                    'resume': resume
                }
                # Add the original name of f as an alias for resume, if it is a valid identifier (e.g. not <lambda>)
                if f.__name__.isidentifier():
                    locals[f.__name__] = resume

                code.interact('Call to {} failed, dropping to console'.format(f.__name__),
                              local=locals,
                              exitmsg='Resuming execution')
                if sys.stdin is empty_stdin:
                    sys.stdin = orig_stdin
    return wrapper


def try_again(f):
    pass


