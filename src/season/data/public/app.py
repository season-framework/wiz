import os
PATH_CWD = os.path.dirname(os.path.dirname(__file__))
os.chdir(PATH_CWD)
import season
ismain = __name__ == '__main__'
app, socketio = season.bootstrap(ismain=ismain)