import season
import os
from argh import arg
import socket

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
frameworkfs = season.util.fs(PATH_FRAMEWORK)

def portchecker(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        port = int(port)
        s.connect(("127.0.0.1", port))
        return True
    except:
        pass
    return False

@arg('projectname', default='sample-project', help='project name')
@arg('--template', default='pug', help='template engine: pug or html (default: pug)')
def create(projectname, template='pug'):
    PATH_PROJECT = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(PATH_PROJECT):
        print("Already exists project path '{}'".format(PATH_PROJECT))
        return
    
    # template 옵션 검증
    if template not in ['html', 'pug']:
        print("Invalid template option. Use 'html' or 'pug'")
        return
    
    fs = season.util.fs(PATH_PROJECT)

    print("create project...")
    PATH_PUBLIC_SRC = os.path.join(PATH_FRAMEWORK, 'data', "websrc")
    fs.copy(PATH_PUBLIC_SRC, PATH_PROJECT)

    startport = 3000
    while portchecker(startport):
        startport = startport + 1
    
    data = fs.read(os.path.join('config', 'boot.py'))
    data = data.replace("__PORT__", str(startport))
    fs.write(os.path.join('config', 'boot.py'), data)
    
    # build.py에 template 정보 저장
    build_config = f"template = '{template}'\n"
    fs.write(os.path.join('config', 'build.py'), build_config)

    print("install ide...")
    fs.copy(os.path.join(PATH_FRAMEWORK, 'data', "ide"), "ide")
    fs.copy(os.path.join(PATH_FRAMEWORK, 'data', "plugin"), "plugin")

    # template engine에 따라 plugin 파일 수정
    if template == 'html':
        # explore/service.ts 수정
        explore_service_path = os.path.join("plugin", "workspace", "app", "explore", "service.ts")
        if fs.exists(explore_service_path):
            content = fs.read(explore_service_path)
            content = content.replace('view.pug', 'view.html')
            content = content.replace("name: 'Pug'", "name: 'HTML'")
            content = content.replace("language: 'pug'", "language: 'html'")
            fs.write(explore_service_path, content)
        
        # portal/service.ts 수정
        portal_service_path = os.path.join("plugin", "workspace", "app", "portal", "service.ts")
        if fs.exists(portal_service_path):
            content = fs.read(portal_service_path)
            content = content.replace('view.pug', 'view.html')
            content = content.replace("name: 'Pug'", "name: 'HTML'")
            content = content.replace("language: 'pug'", "language: 'html'")
            fs.write(portal_service_path, content)

    fs.makedirs(os.path.join(PATH_PROJECT, "project"))
    
    print("build ide...")
    app = season.server(PATH_PROJECT)
    wiz = app.wiz()
    wiz.ide.build.clean()
    wiz.ide.build()

