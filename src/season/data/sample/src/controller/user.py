import season
import datetime
import json
import os

class Controller(wiz.controller("base")):
    def __init__(self):
        super().__init__()
        
        if wiz.session.has("id") == False:
            wiz.response.status(401)
