import inspect

def call(fn, **kwargs):
    args = inspect.getfullargspec(fn).args
    if len(args) > 0:
        if args[0] == 'self':
            args = args[1:]

    for i in range(len(args)):
        key = args[i]
        if key in kwargs: 
            args[i] = kwargs[key]
        else:
            args[i] = None
    
    return fn(*args)

def dummy():
    return