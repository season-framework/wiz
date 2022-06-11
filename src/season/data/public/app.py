import os
import sys
PATH_CWD = os.path.dirname(os.path.dirname(__file__))
os.chdir(PATH_CWD)
import season

server = season.Server()
if __name__ == '__main__':
    server.run()

app = server.wsgi.flask