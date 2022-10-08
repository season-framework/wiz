import os
import sys
PATH_CWD = os.path.dirname(os.path.dirname(__file__))
os.chdir(PATH_CWD)
import season

app = season.app(path=PATH_CWD)
if __name__ == '__main__':
    app.run()

app = app.wsgi()