import inspect
import season

class compiler:
    def __init__(self, fn=None):
        self.fn = fn
    
    def build(self, code, name=None, logger=print, **kwargs):
        fn = {'__file__': name, '__name__': name, 'print': logger, 'season': season}
        for key in kwargs: fn[key] = kwargs[key]
        if type(code) == str:
            exec(compile(code, name, 'exec'), fn)
        else:
            exec(code, fn)
        self.fn = fn
        return self
    
    def __call__(self, **kwargs):
        return self.call(**kwargs)

    def call(self, **kwargs):
        if self.fn is None:
            raise Exception("Compiler is not initialized")
        
        fn = self.fn
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