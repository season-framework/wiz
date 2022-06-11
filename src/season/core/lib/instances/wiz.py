import os
import time

import season

from season.component.obj import InstanceObject

from season.component.wiz.request import Request
from season.component.wiz.response import Response

from season.component.wiz.app import App
from season.component.wiz.route import Route
from season.component.wiz.config import Config
from season.component.wiz.compiler import Compiler
from season.component.wiz.theme import Theme

class wiz(InstanceObject):
    def __init__(self, server, **kwargs):
        self.baseurl = "/"
        super().__init__(server, **kwargs)

    def initialize(self):
        self.request = Request(self)
        self.response = Response(self)
        self.route = Route(self)
        self.app = App(self)
        self.compiler = Compiler(self)
        self.theme = Theme(self)

    def config(self, namespace="config"):
        branch = self.branch()
        c = Config.load(self, branch, namespace)
        return c

    def basepath(self):
        branch = self.branch()
        return os.path.join(season.path.project, 'branch', branch)
        
    def tag(self):
        return "wiz"

    def clean(self):
        path = os.path.join(season.path.project, 'cache', 'branch')
        fs = season.util.os.FileSystem(path)
        fs.remove()