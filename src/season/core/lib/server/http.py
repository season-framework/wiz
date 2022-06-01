import os
import season
import time
import traceback
from werkzeug.exceptions import HTTPException

from season.core.lib.server.handler.http import trigger
from season.core.lib.server.handler.http import app
from season.core.lib.server.handler.http import plugin

class HTTP:
    def __init__(self, server):
        trigger.Trigger(server)
        trigger.Response(server)
        trigger.Error(server)

        app.Resources(server)
        app.Router(server)
        
        plugin.Index(server)
        plugin.API(server)
        plugin.Resources(server)
        plugin.Router(server)