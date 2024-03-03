class Cache:
    def __init__(self, store=dict()):
        self.store = store
    
    def set(self, key, value):
        try:
            self.store[key] = value
        except:
            pass
    
    def get(self, key, default=None):
        try:
            if key in self.store:
                return self.store[key]
        except:
            pass
        if default is not None:
            self.set(key, default)
        return default

    def has(self, key):
        try:
            if key in self.store:
                return True
        except:
            pass
        return False

    def delete(self, key):
        try:
            if key in self.store:
                del self.store[key]
        except:
            pass

    def keys(self):
        return [key for key in self.store]
    
    def clear(self):
        self.store = dict()
