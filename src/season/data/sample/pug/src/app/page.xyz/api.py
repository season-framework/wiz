def status(segment):
    text = wiz.request.query('text', 'hello')
    wiz.response.status(200, text)
