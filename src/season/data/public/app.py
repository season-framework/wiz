import os
PATH_CWD = os.path.dirname(os.path.dirname(__file__))
os.chdir(PATH_CWD)
import season
import flask
app = flask.Flask(__name__, static_url_path='')
ismain = __name__ == '__main__'
app = season.bootstrap(app, ismain)