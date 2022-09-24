class ResponseException(Exception):
    def __init__(self, code=200, response=None):
        super().__init__("season.core.exception.response")
        self.code = code
        self.response = response

    def get_response(self):
        return self.code, self.response

class ErrorException(Exception):
    def __init__(self):
        super().__init__("season.core.exception.error")
        self.code = 500

    def get_response(self):
        return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500

class CompileException(Exception):
    def __init__(self, filename):
        super().__init__(filename)
        self.code = 500
        self.filename = filename

    def get_response(self):
        return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500

