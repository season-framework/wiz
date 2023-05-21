import season
import datetime
import json
import os

class Controller:
    def __init__(self):
        wiz.session = wiz.model("session").use()
        sessiondata = wiz.session.get()
        wiz.response.data.set(session=sessiondata)

        lang = wiz.request.query("lang", None)
        if lang is not None:
            wiz.response.lang(lang)
            wiz.response.redirect(wiz.request.uri())

    def json_default(self, value):
        if isinstance(value, datetime.date):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')
