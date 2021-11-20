class segment:
    def __init__(self, framework):
        self.framework = framework
    
    def get(self, key, _default=None):
        _segment = []
        if len(self.framework.segmentpath) > 0:
            _segment = self.framework.segmentpath.split('/')
        
        if isinstance(key, int):
            if len(_segment) > key:
                return _segment[key]
            
        key = str(key)
        key_loc = len(_segment)
        for i in range(len(_segment)):
            k = _segment[i]
            if k == key:
                key_loc = i
            if i > key_loc:
                return k
        
        if _default is True:
            self.framework.flask.abort(400)

        return _default

    def path(self):
        return self.framework.segmentpath
