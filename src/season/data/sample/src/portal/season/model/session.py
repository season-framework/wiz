class Session:
    def __init__(self):
        self.flask = wiz.server.package.flask
    
    def has(self, key):
        if key in self.flask.session:
            return True
        return False
    
    def delete(self, key):
        self.flask.session.pop(key)
    
    def set(self, **kwargs):
        for key in kwargs:
            self.flask.session[key] = kwargs[key]
    
    def get(self, key=None, default=None):
        if key is None:
            return self.to_dict()
        if key in self.flask.session:
            return self.flask.session[key]
        return default

    def clear(self):
        self.flask.session.clear()

    def to_dict(self):
        return season.util.stdClass(dict(self.flask.session))

    def user_id(self):
        config = wiz.model("portal/season/config")
        session_user_id = config.session_user_id
        return session_user_id(wiz)
    
    def create(self, key):
        config = wiz.model("portal/season/config")
        config.session_create(wiz, key)

    @classmethod
    def use(cls):
        return cls()

Model = Session()
