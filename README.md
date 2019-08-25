# PlsNoCrash
[![Build Status](https://travis-ci.org/HenryWConklin/plsnocrash.svg?branch=master)](https://travis-ci.org/HenryWConklin/plsnocrash)
[![codecov](https://codecov.io/gh/HenryWConklin/plsnocrash/branch/master/graph/badge.svg)](https://codecov.io/gh/HenryWConklin/plsnocrash)

## Setup
This package has no dependencies, you can install it with pip:

```pip install plsnocrash```

## Let Me Try
Have you ever had some compute-intensive code run for hours only for it to crash right
at the end for some inane reason? I have, and it's usually the bit where I save the data
because I used a file path instead of a file object, or mixed up the order of the parameters
for `pickle.dump`. 

Instead of letting all your data go up in smoke, use the `@let_me_try` decorator. It will
drop you to an interactive interpreter if the code you mark raises an exception. It will
also give you access to the variables in the offending function's scope, as well as all
the variables in the scope of every other function on the call stack. From there
you can fix whatever the issue was and resume execution as if nothing even happened.


Here's an example:

```
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

Use save(arg1, ...) or resume(arg1, ...) to call the function again with the given arguments and resume execution.
If the function raises another exception, you will end up at another console.

Use skip(return_value) to skip the function call and resume execution as if it had returned 'return_value'.

Global and local variables are available for all scopes on the call stack under the list call_stack. 
e.g. call_stack[0]['x'] returns the variable 'x' from save (the failing function), 
 and call_stack[1]['y'] returns the variable 'y' from the function that called save.

The original positional arguments are available as the tuple 'args', 
and keyword arguments are available as the dictionary 'kwargs'.

Use quit() or exit() to give up and stop the whole program.



>>> import pickle
>>> pickle.dump(args[0], open('test.pkl','wb'))
>>> skip()
Call skipped
>>>
Resuming execution
All done!
root@710027b06106:/plsnocrash/examples# ls
test.pkl
```

## Retry

Also available is the `@retry(limit=n)` decorator which will rerun a function until it succeeds or 
gives up after `n` retries.

```
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
```
