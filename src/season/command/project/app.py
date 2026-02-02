import os
import json
from .base import BaseCommand


class AppCommand(BaseCommand):
    """App 관리 명령어"""
    
    def list(self, project="main", package=None):
        """앱 목록 조회"""
        if not self._validate_project_path():
            return
        
        base_path = self._get_app_base_path(project, package)
        if not self.fs.isdir(base_path):
            print(f"No apps found in '{base_path}'.")
            return
        
        apps = self.fs.list(base_path)
        print(f"Apps in '{base_path}':")
        for app in apps:
            print(f"  - {app}")
    
    def create(self, namespace=None, project="main", package=None, engine="html", mode="page"):
        """
        앱 생성
        - namespace: 앱 네임스페이스 (예: main.dashboard)
        - project: 프로젝트명 (기본: main)
        - package: 포탈 패키지명 (없으면 src/app, 있으면 portal/<package>/app)
        - engine: 템플릿 엔진 (html, pug)
        - mode: 앱 모드 (page, component, layout)
        """
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Namespace is required. (--namespace=main.dashboard)")
            return
        
        base_path = self._get_app_base_path(project, package)
        app_path = os.path.join(base_path, self._namespace_to_path(namespace))
        
        if self.fs.isdir(app_path):
            print(f"App '{namespace}' already exists at '{app_path}'.")
            return
        
        print(f"Creating app '{namespace}' at '{app_path}'...")
        self.fs.makedirs(app_path)
        
        # app.json 생성
        app_data = {
            "mode": mode,
            "id": namespace,
            "title": namespace,
            "namespace": namespace,
            "viewuri": "/" + namespace.replace(".", "/"),
            "category": "",
            "controller": "",
            "template": ""
        }
        self.fs.write(os.path.join(app_path, "app.json"), json.dumps(app_data, indent=4))
        
        # view.ts 생성
        view_ts = """import { OnInit, Input } from '@angular/core';

export class Component implements OnInit {
    @Input() title: any;

    public async ngOnInit() {
    }
}"""
        self.fs.write(os.path.join(app_path, "view.ts"), view_ts)
        
        # view.[engine] 생성
        if engine == 'pug':
             self.fs.write(os.path.join(app_path, "view.pug"), "div\n    span {{title}}")
        else:
             self.fs.write(os.path.join(app_path, "view.html"), "<div>\n    <span>{{title}}</span>\n</div>")
        
        print(f"App '{namespace}' created successfully.")
    
    def delete(self, namespace=None, project="main", package=None):
        """앱 삭제"""
        if not self._validate_project_path():
            return
        
        if namespace is None:
            print("Namespace is required.")
            return
        
        base_path = self._get_app_base_path(project, package)
        app_path = os.path.join(base_path, self._namespace_to_path(namespace))
        
        if not self.fs.isdir(app_path):
            print(f"App '{namespace}' does not exist.")
            return
        
        print(f"Deleting app '{namespace}'...")
        self.fs.remove(app_path)
        print(f"App '{namespace}' deleted successfully.")
    

