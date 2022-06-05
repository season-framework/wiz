import season

def bootstrap(*args, **kwargs):
    server = season.Server()
    server.run()
    