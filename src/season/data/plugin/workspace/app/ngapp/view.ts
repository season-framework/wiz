import $ from 'jquery';

const DEFAULT_COMPONENT = `import { OnInit, Input } from '@angular/core';

export class Replacement implements OnInit {
    @Input() title: any;

    public async ngOnInit() {
    }
}`.replace('Replacement', 'Component');

const DEFAULT_API = ``;

const DEFAULT_SOKCET = `class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self, wiz, flask):
        print(flask.session)
        pass

    def join(self, flask, data, io):
        sid = flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.join(room)

    def leave(self, flask, data, io):
        sid = flask.request.sid
        if 'id' not in data: return
        room = data['id']
        io.leave(room)

    def disconnect(self, flask, io):
        sid = flask.request.sid
`;

import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';
import toastr from "toastr";

import InfoEditor from "@wiz/app/workspace.editor.ngapp.info";
import PageInfoEditor from "@wiz/app/workspace.editor.ngapp.page";
import MonacoEditor from "@wiz/app/core.editor.monaco";

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
    @Input() mode: any;

    public APP_ID: string = wiz.namespace;
    public keyword: string = "";
    public categories: Array<string> = [];
    public apps: any = {};
    public infoEditorClass: any;

    constructor(private service: Service) { }

    public async ngOnInit() {
        if (this.mode == 'page') this.infoEditorClass = PageInfoEditor;
        else this.infoEditorClass = InfoEditor;

        await this.load();
    }

    public drag(event: any, item: any) {
        event.dataTransfer.setData("text", item.template ? item.template : '');
    }

    public active(item: any) {
        let em = this.service.editor;
        if (!em.activated) return '';
        if (this.APP_ID != em.activated.component_id) return '';
        if (item.id != em.activated.subtitle) return '';
        return 'active';
    }

    public match(item: any) {
        if (!this.keyword) return true;
        if (item.title)
            if (item.title.toLowerCase().indexOf(this.keyword.toLowerCase()) >= 0)
                return true;

        if (item.id) {
            let target = item.id.toLowerCase().substring(this.mode.length);
            if (target.toLowerCase().indexOf(this.keyword.toLowerCase()) >= 0) {
                return true;
            }
        }
        return false;
    }

    public async load() {
        let { data } = await wiz.call("list", { mode: this.mode });
        let apps: any = {};
        let categories: any = [];
        for (let i = 0; i < data.length; i++) {
            let app = data[i];
            let category = app.category;
            if (!category) category = 'undefined';
            if (!apps[category]) {
                apps[category] = [];
                if (categories.indexOf(category) < 0)
                    categories.push(category)
            }
            apps[category].push(app);
        }

        this.apps = apps;
        this.categories = categories.sort();

        await this.service.render();
    }

    private async update(path: string, data: string, entire: boolean = false, viewuri: string | null = null) {
        let res = await wiz.call('update', { path: path, code: data });
        toastr.success("Updated");
        await this.load();
        res = await wiz.call('build', { path: path, entire: entire });
        if (res.code == 200) toastr.info("Build Finish");
        else toastr.error("Error on build");
        if (!viewuri) return;
        let binding = this.service.event.load("season.preview");
        if (binding) await binding.move(viewuri);
    }

    public async create() {
        // create editor
        let editor = this.service.editor.create({ component_id: this.APP_ID, title: 'New' });

        // create tab
        editor.create({ name: 'info', viewref: this.infoEditorClass })
            .bind('data', async (tab) => {
                return { mode: this.mode, id: '', title: '', namespace: '', viewuri: '', category: '' };
            }).bind('update', async (tab) => {
                let data = await tab.data();
                let check = /^[a-z0-9.]+$/.test(data.namespace);
                if (!check) return toastr.error("invalidate namespace");
                if (data.namespace.length < 3) return toastr.error("namespace at least 3 alphabets");

                let id = data.mode + "." + data.namespace;
                let res = await wiz.call("exists", { id });
                if (res.data) return toastr.error("namespace already exists");

                data.id = id;
                data = JSON.stringify(data, null, 4);
                let path = "app/" + id + "/app.json";

                editor.close();
                await wiz.call('update', { path, code: data });
                await this.load();
            });

        await editor.open();
    }

    public async open(app: any, location: number = -1) {
        let apppath = 'app/' + app.id;
        let mode = this.mode;

        // create editor
        let editor = this.service.editor.create({
            component_id: this.APP_ID,
            path: apppath,
            title: app.title ? app.title : app.namespace,
            subtitle: app.id,
            current: 1
        });

        // create tab
        editor.create({
            name: 'info',
            viewref: this.infoEditorClass,
            path: apppath + "/app.json"
        }).bind('data', async (tab) => {
            let { code, data } = await wiz.call('data', { path: tab.path });
            if (code != 200) return {};
            data = JSON.parse(data);
            data.mode = mode;
            return data;
        }).bind('update', async (tab) => {
            let data = await tab.data();
            let viewuri = data.preview ? data.preview : data.viewuri;

            let check = /^[a-z0-9.]+$/.test(data.namespace);
            if (!check) return toastr.error("invalidate namespace");
            if (data.namespace.length < 3) return toastr.error("namespace at least 3 alphabets");

            let from = data.id + '';
            let to = data.mode + "." + data.namespace;

            // if moved
            if (from != to) {
                let res = await wiz.call("move", { from, to });
                if (res.code == 400) {
                    toastr.error("invalidate namespace");
                    return;
                }
            }

            data.id = to
            editor.modify({ path: 'app/' + to, title: data.title ? data.title : data.namespace, subtitle: to });

            for (let i = 0; i < editor.tabs.length; i++) {
                let topath: any = editor.tabs[i].path + '';
                topath = topath.split("/");
                topath[1] = to;
                topath = topath.join("/");
                editor.tabs[i].move(topath);
            }

            data = JSON.stringify(data, null, 4);
            await this.update(editor.path + '/app.json', data, from != to, viewuri);
        });

        // monaco editor tabs
        let tabs: any = [
            editor.create({
                name: 'Pug',
                viewref: MonacoEditor,
                path: apppath + "/view.pug",
                config: { monaco: { language: 'pug' } }
            }),
            editor.create({
                name: 'Component',
                viewref: MonacoEditor,
                path: apppath + "/view.ts",
                config: { monaco: { language: 'typescript', renderValidationDecorations: 'off' } }
            }),
            editor.create({
                name: 'SCSS',
                viewref: MonacoEditor,
                path: apppath + "/view.scss",
                config: { monaco: { language: 'scss' } }
            })
        ];

        if (mode != 'layout') {
            tabs.push(
                editor.create({
                    name: 'API',
                    viewref: MonacoEditor,
                    path: apppath + "/api.py",
                    config: { monaco: { language: 'python' } }
                }),
                editor.create({
                    name: 'Socket',
                    viewref: MonacoEditor,
                    path: apppath + "/socket.py",
                    config: { monaco: { language: 'python' } }
                }));
        }

        // bind event to monaco editor tabs
        for (let i = 0; i < tabs.length; i++) {
            tabs[i].bind('data', async (tab) => {
                editor.meta.info = await editor.tab(0).data();
                let { code, data } = await wiz.call('data', { path: tab.path });
                if (code != 200) return {};

                if (!data) {
                    if (tab.name == 'Component') {
                        data = DEFAULT_COMPONENT;
                    } else if (tab.name == 'API') {
                        data = DEFAULT_API;
                    }
                }

                return { mode, data };
            }).bind('update', async (tab) => {
                let data = await tab.data();
                await this.update(tab.path, data.data, false, editor.meta.info ? (editor.meta.info.preview ? editor.meta.info.preview : editor.meta.info.viewuri) : null);
            });
        }

        // bind editor delete event
        editor.bind("delete", async () => {
            let res = await this.service.alert.show({ title: 'Delete App', message: 'Are you sure remove "' + editor.title + '"?', action_text: "Delete", action_class: "btn-danger" });
            if (res !== true) return;

            let targets = await this.service.editor.find(editor);
            for (let i = 0; i < targets.length; i++)
                await targets[i].close();
            await wiz.call("remove", { path: editor.path });
            await this.load();
            await wiz.call('build', { path: editor.path, entire: true });
        });

        // bind editor clone event
        editor.bind("clone", async (location: number = -1) => {
            await this.open(app, location);
        });

        await editor.open(location);
    }

    public async upload_file() {
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

        let fd = new FormData($('#file-form-app')[0]);
        let { data } = await fn(fd);

        if (data.length > 0) {
            toastr.error('already exists: ' + data.join(", "));
        }

        await this.load();
    }

    public async upload() {
        await this.service.render();
        $('#file-form-app input').click();
    }

}