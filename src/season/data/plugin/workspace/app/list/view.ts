const DEFAULT_GITIGNORE = `cache/
config/
.vscode/
test/

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
#  Usually these files are written by a python script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/
`;

import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

import toastr from "toastr";
import $ from 'jquery';

import MonacoEditor from "@wiz/app/core.editor.monaco";
import WorkspaceInfo from "@wiz/app/workspace.editor.wsinfo";

toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-top-center",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": 300,
    "hideDuration": 500,
    "timeOut": 1500,
    "extendedTimeOut": 1000,
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public current: string = wiz.branch();
    public keyword: string = "";
    public loading: boolean = false;
    public data: any = [];
    public isdev = wiz.dev();

    constructor(private service: Service) {
    }

    public async ngOnInit() {
        await this.load();
    }

    public async load() {
        await this.loader(true);
        let { data } = await wiz.call("list");
        data.sort((a, b) => a.id.localeCompare(b.id));
        this.data = data;
        await this.loader(false);
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public match(item: any) {
        let target = item.id.toLowerCase();
        if (target.indexOf(this.keyword.toLowerCase()) >= 0)
            return true;
        return false;
    }

    public check_validation(name: string) {
        for (let i = 0; i < this.data.length; i++)
            if (name == this.data[i].id)
                return false;
        if (name.length < 3)
            return false;
        if (/^[a-z]+$/.test(name))
            return true;
        return false;
    }

    public async upload_file() {
        let project_id = this.keyword + '';
        if (!this.check_validation(project_id)) {
            toastr.error("invalidate namespace");
            return
        }

        await this.loader(true);

        let fn = (fd) => new Promise((resolve) => {
            let url = wiz.url('upload');
            $.ajax({
                url: url,
                type: 'POST',
                data: fd,
                cache: false,
                contentType: false,
                processData: false
            }).always(function (res) {
                resolve(res);
            });
        });

        let fd = new FormData($('#file-form')[0]);
        fd.append("path", project_id);
        await fn(fd);
        await this.load();
    }

    public async upload() {
        let project_id = this.keyword + '';
        if (!this.check_validation(project_id)) {
            toastr.error("invalidate namespace");
            return
        }
        $('#file-upload').click();
    }

    public async create() {
        let project_id = this.keyword + '';
        if (!this.check_validation(project_id)) {
            toastr.error("invalidate namespace");
            return
        }
        await this.loader(true);
        let { code } = await wiz.call("create", { path: project_id });
        await this.load();
    }

    public async download(item: any) {
        let target = wiz.url("download/" + item.id);
        window.open(target, '_blank');
    }

    public async ng_download(item: any) {
        let target = wiz.url("ng_download/" + item.id);
        window.open(target, '_blank');
    }

    public async open(item: any) {
        let path = item.id;
        await wiz.call("git", { path });

        let editor = this.service.editor.create({
            component_id: this.APP_ID,
            path: '/project/' + path,
            title: 'Project',
            subtitle: path,
            unique: true,
            current: 0
        }).bind('close', async (tab) => {
            await this.load();
        });

        editor.create({
            name: 'setting',
            viewref: WorkspaceInfo,
            path: path + "/wiz.workspace"
        }).bind('data', async (tab) => {
            return { project: path };
        }).bind('update', async (tab) => {

        });

        let createTab = (path: string, lang: string, name: string = "code", dvalue: string = "") => {
            let monaco: any = { language: lang };
            if (lang == 'typescript') monaco.renderValidationDecorations = 'off';

            editor.create({
                name: name,
                viewref: MonacoEditor,
                path: path,
                config: { monaco }
            }).bind('data', async (tab) => {
                let { code, data } = await wiz.call('data', { path: tab.path });
                if (code != 200) return {};
                if (!data) data = dvalue;
                return { data };
            }).bind('update', async (tab) => {
                let data = await tab.data();
                let { code } = await wiz.call('update', { path: tab.path, data: data.data });
                if (code == 200) toastr.success("Updated");
            });
        }

        createTab(path + '/.gitignore', 'conf', 'gitignore', DEFAULT_GITIGNORE);

        await editor.open();
    }
}