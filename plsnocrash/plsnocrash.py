import inspect
import traceback
import code
import sys
from io import StringIO


def get_call_stack():
    frame = inspect.currentframe()
    # Skip this function
    frame = frame.f_back
    # Skip the function that called this function
    frame = frame.f_back

    # Build a list of the locals in each caller in the stack
    stack = []
    while frame is not None:
        vars = dict(frame.f_globals, **frame.f_locals)
        stack.append(vars)
        frame = frame.f_back

    # Get the vars for the function that failed
    base_frame = inspect.trace()[-1][0]
    base_vars = dict(base_frame.f_globals, **base_frame.f_locals)
    stack.insert(0, base_vars)
    return stack


def build_letmetry_helptext(fname, args, kwargs):
    if fname.isidentifier():
        resume_str = f"{fname}(arg1, ...) or "
    else:
        resume_str = ''
    return f"Call to {fname}(args={args}, kwargs={kwargs}) failed.\n\n" \
        f"Use {resume_str}resume(arg1, ...) to call the function again with the given arguments and resume execution.\n" \
        f"If the function raises another exception, you will end up at another console.\n\n" \
        f"Use skip(return_value) to skip the function call and resume execution as if it had returned 'return_value'.\n\n" \
        f"Global and local variables are avaiable for all scopes on the call stack under the list call_stack. \n" \
        f"e.g. call_stack[0]['x'] returns the variable 'x' from {fname} (the failing function), \nand call_stack[1]['y']" \
        f"returns the variable 'y' from the function that called {fname}."


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

                code.interact(banner=build_letmetry_helptext(f.__name__, args, kwargs),
                              local=locals,
                              exitmsg='Resuming execution')
                if sys.stdin is empty_stdin:
                    sys.stdin = orig_stdin
        # Return the value passed to skip instead of a result from f
        return _ret_val

    return wrapper


def try_again(f):
    pass
