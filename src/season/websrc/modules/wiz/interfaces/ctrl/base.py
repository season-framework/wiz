import season
import datetime
import json
import os
import time
import traceback

class base:
    def __startup__(self, framework):
        self.framework = framework
        self.__framework__ = framework

        self.config = framework.config.load('wiz')
        self.wiz = framework.model("wiz", module="wiz").use()

    def parse_json(self, jsonstr, default=None):
        try:
            return json.loads(jsonstr)
        except:
            pass
        return default

    def json_default(self, value):
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value).replace('<', '&lt;').replace('>', '&gt;')

class view(base):
    def __startup__(self, framework):
        super().__startup__(framework)
        
        self._css = []
        self._js = []
        self._exportjs = {}

        framework.response.data.set(css=self._css)
        framework.response.data.set(js=self._js)
        framework.response.data.set(exportjs=self._exportjs)

        isdevmode = framework.request.query("dev", None)
        if isdevmode is not None:
            if isdevmode == "false" : self.wiz.set_dev("false")
            else: self.wiz.set_dev("true")
            framework.response.redirect(framework.request.uri())

        # change branch after check exist working branch
        branch = framework.request.query("branch", None)
        if branch is not None and len(branch) > 0:
            if branch in framework.wiz.workspace.branches():
                framework.wiz.workspace.checkout(branch)
                framework.response.cookies.set("season-wiz-branch", branch)
            framework.response.redirect(framework.request.uri())
    
    def exportjs(self, **args):
        for key in args:
            v = args[key]
            self._exportjs[key] = json.dumps(v, default=self.json_default)
        self.__framework__.response.data.set(exportjs=self._exportjs)

    def css(self, url):
        framework = self.__framework__
        url = os.path.join(framework.modulename, url)
        self._css.append(url)
        self.__framework__.response.data.set(css=self._css)
    
    def js(self, url):
        framework = self.__framework__
        url = os.path.join(framework.modulename, url)
        self._js.append(url)
        self.__framework__.response.data.set(js=self._js)

    def nav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'active'
                else: menu['class'] = ''

            if 'child' in menu:
                menu['show'] = 'show'
                for i in range(len(menu['child'])):
                    child = menu['child'][i]
                    cpt = None
                
                    if 'pattern' in child: cpt = child['pattern']
                    elif 'url' in child: cpt = child['url']

                    if cpt is not None:
                        if framework.request.match(cpt): 
                            menu['child'][i]['class'] = 'active'
                            menu['show'] = 'show'
                        else: 
                            menu['child'][i]['class'] = ''

        framework.response.data.set(menus=menus)

    def subnav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'bg-dark text-white'
                else: menu['class'] = ''

        framework.response.data.set(submenus=menus)

    def topnav(self, menus):
        framework = self.__framework__

        for menu in menus:
            pt = None
            if 'pattern' in menu: pt = menu['pattern']
            elif 'url' in menu: pt = menu['url']

            if pt is not None:
                if framework.request.match(pt): menu['class'] = 'bg-dark text-white'
                else: menu['class'] = ''

        framework.response.data.set(topmenus=menus)
        
class api(base):
    def __startup__(self, framework):
        super().__startup__(framework)

    def __error__(self, framework, e):
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            errorlog = f"\033[91m[" + timestamp + "}][wiz][error]\n" + traceback.format_exc() + "\033[0m"
            branch = framework.wiz.branch()
            framework.socketio.emit("log", errorlog, namespace="/wiz", to=branch, broadcast=True)
        except:
            print("error")
            pass
        framework.response.status(500, str(e))
