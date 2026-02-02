import season
import os
from argh import arg

from .base import BaseCommand
from .core import ProjectCommand
from .app import AppCommand
from .controller import ControllerCommand
from .model import ModelCommand
from .route import RouteCommand
from .npm import NpmCommand
from .pip_cmd import PipCommand
from .portal import PortalCommand

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


# 명령어 인스턴스들
_project_cmd = ProjectCommand()
_app_cmd = AppCommand()
_controller_cmd = ControllerCommand()
_model_cmd = ModelCommand()
_route_cmd = RouteCommand()
_npm_cmd = NpmCommand()
_pip_cmd = PipCommand()
_portal_cmd = PortalCommand()

# 서브커맨드 매핑
_subcommands = {
    'app': _app_cmd,
    'controller': _controller_cmd,
    'model': _model_cmd,
    'route': _route_cmd,
    'npm': _npm_cmd,
    'pip': _pip_cmd,
    'portal': _portal_cmd,
}

# 프로젝트 기본 액션
_project_actions = ['build', 'create', 'delete', 'list', 'info', 'sync', 'clean']


@arg('subcommand', help="app | controller | model | route | npm | pip | portal | build | create | delete | list | info | sync | clean")
@arg('action', nargs='?', help="action for subcommand (create, delete, list, update, etc.)")
@arg('--project', help='project name')
@arg('--uri', help='git repository URI')
@arg('--path', help='local path to copy from')
@arg('--namespace', help='app namespace (e.g., main.dashboard)')
@arg('--package', help='portal package name')
@arg('--name', help='component name')
@arg('--template', help='template name')
@arg('--version', help='package version')
@arg('--dev', help='install as dev dependency (npm)')
@arg('--output', help='output file path')
@arg('--input', help='input file path')
@arg('--source', help='source namespace for copy/move')
@arg('--target', help='target namespace for copy/move')
@arg('--methods', help='HTTP methods for route')
@arg('--overwrite', help='overwrite existing')
@arg('--clean', help='clean build cache before building')
def project(subcommand, action, *, project=None, uri=None, path=None, 
            namespace=None, package=None, name=None, template='default',
            version=None, dev=False, output=None, input=None,
            source=None, target=None, methods=None, overwrite=False, clean=False):
    """
    WIZ Project Management
    
    Usage:
        # Project commands
        wiz project build --project=main
        wiz project create --project=dev
        wiz project create --project=dev --uri=<git_uri>
        wiz project create --project=dev --path=<file_path>
        wiz project delete --project=dev
        wiz project list
        wiz project info --project=main
        
        # App commands
        wiz project app list [--package=portal_name]
        wiz project app create --namespace=main.dashboard [--package=portal_name]
        wiz project app delete --namespace=main.dashboard
        wiz project app export --namespace=main.dashboard
        wiz project app import --uri=main.dashboard.wizapp
        wiz project app copy --source=main.old --target=main.new
        wiz project app move --source=main.old --target=main.new
        
        # Controller commands
        wiz project controller list [--package=portal_name]
        wiz project controller create --name=api [--package=portal_name]
        wiz project controller delete --name=api
        
        # Model commands
        wiz project model list [--package=portal_name]
        wiz project model create --name=user [--package=portal_name]
        wiz project model delete --name=user
        
        # Route commands
        wiz project route list [--package=portal_name]
        wiz project route create --name=api --path=/api [--package=portal_name]
        wiz project route delete --name=api
        
        # NPM commands
        wiz project npm list
        wiz project npm install --package=@angular/core --version=^18.2.5
        wiz project npm uninstall --package=@angular/core
        wiz project npm update [--package=@angular/core]
        
        # PIP commands
        wiz project pip list
        wiz project pip install --package=dizest --version=4.0.15
        wiz project pip uninstall --package=dizest
        wiz project pip import [--input=requirements.txt]
        wiz project pip export [--output=requirements.txt]
        
        # Portal commands
        wiz project portal list
        wiz project portal create --name=myportal
        wiz project portal delete --name=myportal
        wiz project portal info --name=myportal
    """
    
    # 프로젝트 기본 액션인 경우
    if subcommand in _project_actions:
        fn = getattr(_project_cmd, subcommand)
        if subcommand == 'build':
            fn(project=project or "main", clean=clean)
        elif subcommand == 'create':
            fn(project=project or "demo", uri=uri, path=path)
        elif subcommand == 'delete':
            fn(project=project)
        elif subcommand == 'list':
            fn()
        elif subcommand == 'info':
            fn(project=project or "main")
        elif subcommand == 'sync':
            fn(project=project or "main")
        elif subcommand == 'clean':
            fn(project=project or "main")
        return
    
    # 서브커맨드 처리
    if subcommand not in _subcommands:
        print(f"Unknown subcommand: {subcommand}")
        print("Available subcommands: app, controller, model, route, npm, pip, portal")
        print("Available actions: build, create, delete, list, info, sync, clean")
        return
    
    cmd = _subcommands[subcommand]
    
    if action is None:
        print(f"Action is required for '{subcommand}' subcommand.")
        cmd.help()
        return
    
    if not hasattr(cmd, action):
        print(f"Unknown action: {action}")
        cmd.help()
        return
    
    fn = getattr(cmd, action)
    
    # 각 서브커맨드별 파라미터 전달
    if subcommand == 'app':
        if action == 'create':
            fn(namespace=namespace, package=package, template=template)
        elif action == 'delete':
            fn(namespace=namespace, package=package)
        elif action == 'list':
            fn(package=package)
        elif action == 'update':
            fn(namespace=namespace, package=package)
        elif action == 'export':
            fn(namespace=namespace, package=package, output=output)
        elif action == 'import':
            fn(uri=uri, package=package, overwrite=overwrite)
        elif action == 'copy':
            fn(source=source, target=target, package=package)
        elif action == 'move':
            fn(source=source, target=target, package=package)
        else:
            fn()
    
    elif subcommand == 'controller':
        if action == 'create':
            fn(name=name, package=package, template=template)
        elif action == 'delete':
            fn(name=name, package=package)
        elif action == 'list':
            fn(package=package)
        elif action == 'update':
            fn(name=name, package=package)
        else:
            fn()
    
    elif subcommand == 'model':
        if action == 'create':
            fn(name=name, package=package, template=template)
        elif action == 'delete':
            fn(name=name, package=package)
        elif action == 'list':
            fn(package=package)
        elif action == 'update':
            fn(name=name, package=package)
        else:
            fn()
    
    elif subcommand == 'route':
        if action == 'create':
            fn(name=name, package=package, route_path=path or "/", methods=methods, template=template)
        elif action == 'delete':
            fn(name=name, package=package)
        elif action == 'list':
            fn(package=package)
        elif action == 'update':
            fn(name=name, package=package)
        else:
            fn()
    
    elif subcommand == 'npm':
        if action == 'install':
            fn(package=package, version=version, dev=dev)
        elif action == 'uninstall':
            fn(package=package)
        elif action == 'list':
            fn()
        elif action == 'update':
            fn(package=package)
        else:
            fn()
    
    elif subcommand == 'pip':
        if action == 'install':
            fn(package=package, version=version)
        elif action == 'uninstall':
            fn(package=package)
        elif action == 'list':
            fn()
        elif action == 'export':
            fn(output=output or "requirements.txt")
        elif action == 'import':
            fn(input_file=input or "requirements.txt")
        else:
            fn()
    
    elif subcommand == 'portal':
        if action == 'create':
            fn(name=name)
        elif action == 'delete':
            fn(name=name)
        elif action == 'list':
            fn()
        elif action == 'info':
            fn(name=name)
        else:
            fn()
