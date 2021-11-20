import os
import season
import json

class Controller(season.interfaces.wiz.ctrl.admin.branch.api):

    def __startup__(self, framework):
        super().__startup__(framework)

    def diff(self, framework):
        branch = framework.request.segment.get(0, True)
        branch = branch.split("_")
        base_branch = branch[1]
        branch = branch[0]

        merge = framework.wiz.workspace.merge().checkout(branch, base_branch)
        diff = merge.diff()

        res = dict()
        res['apps'] = []
        res['routes'] = []
        res['files'] = []
        apps = dict()
        
        def parser_app(dif):
            try:
                parent_path = dif['parent_path']
                parent = str(dif['parent'])
                if parent == "index": parent = None

                commit_path = dif['commit_path']
                commit = str(dif['commit'])
                if commit == "index": commit = None

                try:
                    app_id = commit_path.split("/")[1]
                    category = commit_path.split("/")[0]
                except:
                    app_id = parent_path.split("/")[1]
                    category = parent_path.split("/")[0]
                
                if category not in ['apps', 'routes']:
                    return False
                    
                display = f"{category}/{app_id}"

                change_type = 'M'

                commit_route = None
                commit_namespace = None
                try:
                    commit_appinfo = json.loads(merge.file(f"{display}/app.json"))
                    commit_namespace = commit_appinfo['namespace']
                    if 'route' in commit_appinfo: commit_route = commit_appinfo['route']
                except:
                    commit_appinfo = None
                
                parent_route = None
                parent_namespace = None
                try:
                    parent_appinfo = merge.file(f"{display}/app.json", commit=parent)
                    parent_appinfo = json.loads(parent_appinfo)
                    parent_namespace = parent_appinfo['namespace']
                    if 'route' in parent_appinfo: parent_route = parent_appinfo['route']
                except Exception as e:
                    parent_appinfo = None

                if commit_appinfo is None and parent_appinfo is not None: 
                    change_type = 'D'
                if commit_appinfo is not None and parent_appinfo is None: 
                    change_type = 'A'

                if display not in apps:
                    apps[display] = dict()
                    apps[display]['change_type'] = change_type
                    apps[display]['commit'] = commit
                    apps[display]['parent'] = parent
                    apps[display]['commit_path'] = display
                    apps[display]['parent_path'] = display
                    apps[display]['display'] = display
                    if commit_route is not None: apps[display]['display'] = commit_route
                    elif parent_route is not None: apps[display]['display'] = parent_route
                    elif commit_namespace is not None: apps[display]['display'] = commit_namespace
                    elif parent_namespace is not None: apps[display]['display'] = parent_namespace
                    apps[display]['category'] = category
                    apps[display]['commit_namespace'] = commit_namespace
                    apps[display]['parent_namespace'] = parent_namespace
                return True
            except Exception as e:
                return False
                        
        for i in range(len(diff)):
            change_type = diff[i]['change_type']
            parent_path = diff[i]['parent_path']
            commit_path = diff[i]['commit_path']

            if parent_path is None and commit_path is None:
                continue

            stat = parser_app(diff[i])
            if stat:
                continue
            
            diff[i]['display'] = diff[i]['commit_path'].split("/")[-1]
            res['files'].append(diff[i])

        for app_id in apps:
            res[apps[app_id]['category']].append(apps[app_id])

        total = 0
        for key in res:
            total += len(res[key])
        
        res['count'] = total
        framework.response.status(200, res)

    def commit(self, framework):
        branch = framework.request.segment.get(0, True)
        branch = branch.split("_")
        base_branch = branch[1]
        branch = branch[0]
        merge = framework.wiz.workspace.merge().checkout(branch, base_branch)
        message = framework.request.query('message', f'Merge branch `{branch}` into `{base_branch}`')
        if len(message) == 0:
            message = f'Merge branch `{branch}` into `{base_branch}`'
        merge.commit(message=message)
        merge.delete()
        framework.response.status(200)

    def update(self, framework):
        branch = framework.request.segment.get(0, True)
        path = framework.request.query('path', True)
        fs = framework.model("wizfs", module="wiz").use(f"wiz/merge/{branch}")
        fs.write(path, data)
        framework.response.status(200)

    def delete(self, framework):
        branch = framework.request.segment.get(0, True)
        data = framework.request.query('data', '')
        path = framework.request.query('path', True)
        fs = framework.model("wizfs", module="wiz").use(f"wiz/merge/{branch}")
        fs.delete(path)
        framework.response.status(200)

    def file(self, framework):
        branch = framework.request.segment.get(0, True)
        commit = framework.request.segment.get(1, "")
        filepath = framework.request.query("filepath", True)

        branch = branch.split("_")
        base_branch = branch[1]
        branch = branch[0]

        merge = framework.wiz.workspace.merge().checkout(branch, base_branch)

        if commit is not None and len(commit) == 0:
            commit = None

        extmap = framework.config.load("wiz").get("supportfiles", {})

        category = filepath.split("/")[0]

        def load_app_files(key):
            try:
                appfile = os.path.join(filepath, key)
                text = merge.file(appfile, commit=commit)
                return text
            except:
                return ""

        if category in ['apps', 'routes']:
            appinfo = dict()
            try:
                appinfo = os.path.join(filepath, 'app.json')
                appinfo = merge.file(appinfo, commit=commit)
                appinfo_txt = appinfo
                appinfo = json.loads(appinfo)
                appinfo['info'] = appinfo_txt
                appinfo["controller"] = load_app_files("controller.py")
                appinfo["dic"] = load_app_files("dic.json")
                if category == 'apps':
                    appinfo["api"] = load_app_files("api.py")
                    appinfo["socketio"] = load_app_files("socketio.py")
                    appinfo["html"] = load_app_files("html.dat")
                    appinfo["js"] = load_app_files("js.dat")
                    appinfo["css"] = load_app_files("css.dat")
            except:
                pass
            framework.response.status(200, mode=category, app=appinfo)
        
        _, ext = os.path.splitext(filepath)
        ext = ext.lower()
        if ext not in extmap:
            framework.response.status(400)

        language = extmap[ext]
        text = merge.file(filepath, commit=commit)
        framework.response.status(200, mode="text", text=text, language=language)