class status(Exception):
    def __init__(self, code=200, response=None):
        super().__init__("season.core.CLASS.RESPONSE.STATUS")
        self.code = code
        self.response = response

    def get_response(self):
        return self.response, self.code