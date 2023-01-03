import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

import $ from 'jquery';
import toastr from "toastr";

import { FlatTreeControl } from '@angular/cdk/tree';
import { FileNode, FileDataSource } from './service';

import MonacoEditor from "@wiz/app/core.editor.monaco";
import PageInfoEditor from "@wiz/app/workspace.editor.ngapp.page";
import AppInfoEditor from "@wiz/app/workspace.editor.ngapp.info";
import RouteInfoEditor from "@wiz/app/workspace.editor.route";

const DEFAULT_COMPONENT = `import { OnInit, Input } from '@angular/core';

export class Replacement implements OnInit {
    @Input() title: any;

    public async ngOnInit() {
    }
}`.replace('Replacement', 'Component');

const DEFAULT_API = ``;

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

@dependencies({
    MatTreeModule: '@angular/material/tree'
})
export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public path: string = 'src';

    public color = '';

    public APP_ID: string = wiz.namespace;
    public loading: boolean = false;
    public rootNode: FileNode;

    private treeControl: FlatTreeControl<FileNode>;
    private dataSource: FileDataSource;
    private getLevel = (node: FileNode) => node.level;
    private isExpandable = (node: FileNode) => node.extended;

    public isFolder = (_: number, node: FileNode) => node.type == 'folder';
    public isMod = (_: number, node: FileNode) => node.type.substring(0, 3) == 'mod';
    public isNew = (_: number, node: FileNode) => node.type == 'new.folder' || node.type == 'new.file';
    public isRoot = (node: FileNode) => node.parent == this.rootNode;

    constructor(private service: Service) { }

    public drag(event: any, node: any) {
        event.dataTransfer.setData("text", node.meta.template);
    }

    public active(node: FileNode | null) {
        try {
            if (this.service.editor.activated) {
                let targetpath = this.service.editor.activated.tab().path;
                if (targetpath.startsWith('src/app') || targetpath.startsWith('src/route')) {
                    if (targetpath.split("/")[2] == node.path.split("/")[2]) {
                        return true;
                    }
                }

                if (targetpath == node.path) {
                    return true;
                }
            }
        } catch (e) {
        }
        return false;
    }

    public async list(node: FileNode) {
        let { code, data } = await wiz.call("list", { path: node.path });
        data = data.map(item => new FileNode(item.name, item.path, item.type, node, node.level + 1, item.meta ? item.meta : {}));
        data.sort((a, b) => {
            if (node.level === -1)
                return 0;
            if (a.type == b.type)
                return a.path.localeCompare(b.path);
            if (a.type == 'folder') return -1;
            if (b.type == 'folder') return 1;
        });
        return data;
    }

    private async update(path: string, data: string, node: any = null) {
        let res = await wiz.call('update', { path: path, code: data });
        if (node) await this.refresh(node, false);
        if (["route", "controller", "model", "config"].includes(path.split("/")[1])) {
            if (res.code == 200) toastr.info("Updated");
            return
        }

        if (res.code == 200) toastr.success("Updated");
        res = await wiz.call('build', { path: path });
        if (res.code == 200) toastr.info("Builded");
        else toastr.error("Error on build");
    }

    public async open(node: FileNode, location: number = -1) {
        if (!node) return;
        if (node.editable) return;
        if (node.type.split(".")[0] == "new") return;

        let openEditor = {
            angular: async () => {
                let files = [
                    { name: 'index', path: 'index.pug', lang: 'pug' },
                    { name: 'web resources', path: 'angular.build.options.json', lang: 'json' },
                    { name: 'module', path: 'app/app.module.ts', lang: 'typescript' },
                    { name: 'routing', path: 'app/app-routing.module.ts', lang: 'typescript' },
                    { name: 'wiz', path: 'wiz.ts', lang: 'typescript' }
                ];

                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: node.path,
                    title: 'Angular Config',
                    unique: true,
                    current: 0
                });

                let createTab = (path: string, lang: string, name: string = "code") => {
                    let monaco: any = { language: lang };
                    if (lang == 'typescript') monaco.renderValidationDecorations = 'off';

                    editor.create({
                        name: name,
                        viewref: MonacoEditor,
                        path: path,
                        config: { monaco }
                    }).bind('data', async (tab) => {
                        let { code, data } = await wiz.call('read', { path: tab.path });
                        if (code != 200) return {};
                        return { data };
                    }).bind('update', async (tab) => {
                        let data = await tab.data();
                        await this.update(tab.path, data.data);
                    });
                }

                for (let i = 0; i < files.length; i++)
                    createTab(node.path + "/" + files[i].path, files[i].lang, files[i].name);

                await editor.open();
            },
            app: async () => {
                let app = node.meta;
                let apppath = node.path;
                let mode = app.id.split(".")[0];

                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: apppath,
                    title: app.title ? app.title : app.namespace,
                    subtitle: app.id,
                    current: 1
                });

                editor.namespace_prefix = mode + ".";

                editor.create({
                    name: 'info',
                    viewref: mode == 'page' ? PageInfoEditor : AppInfoEditor,
                    path: node.path + "/app.json"
                }).bind('data', async (tab) => {
                    let { code, data } = await wiz.call('read', { path: tab.path });
                    if (code != 200) return {};
                    data = JSON.parse(data);
                    data.mode = mode;
                    return data;
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.namespace);
                    if (!check) return toastr.error("invalidate namespace");
                    if (data.namespace.length < 3) return toastr.error("namespace at least 3 alphabets");

                    let from = data.id + '';
                    let to = data.mode + "." + data.namespace;

                    if (from != to) {
                        node.rename = to;
                        let res = await this.move(node);
                        if (!res) {
                            toastr.error("invalidate namespace");
                            return;
                        }
                    }

                    node.path = node.path.split("/")
                    node.path[2] = to;
                    node.path = node.path.join("/");

                    data.id = to;
                    editor.modify({ path: node.path, title: data.title ? data.title : data.namespace, subtitle: to });

                    for (let i = 0; i < editor.tabs.length; i++) {
                        let topath: any = editor.tabs[i].path + '';
                        topath = topath.split("/");
                        topath[2] = to;
                        topath = topath.join("/");
                        editor.tabs[i].move(topath);
                    }

                    node.name = data.title;
                    data = JSON.stringify(data, null, 4);
                    await this.update(node.path + '/app.json', data, node);
                });

                let tabs: any = [
                    editor.create({
                        name: 'Pug',
                        viewref: MonacoEditor,
                        path: node.path + "/view.pug",
                        config: { monaco: { language: 'pug' } }
                    }),
                    editor.create({
                        name: 'Component',
                        viewref: MonacoEditor,
                        path: node.path + "/view.ts",
                        config: { monaco: { language: 'typescript', renderValidationDecorations: 'off' } }
                    }),
                    editor.create({
                        name: 'SCSS',
                        viewref: MonacoEditor,
                        path: node.path + "/view.scss",
                        config: { monaco: { language: 'scss' } }
                    }),
                    editor.create({
                        name: 'API',
                        viewref: MonacoEditor,
                        path: node.path + "/api.py",
                        config: { monaco: { language: 'python' } }
                    }),
                    editor.create({
                        name: 'Socket',
                        viewref: MonacoEditor,
                        path: node.path + "/socket.py",
                        config: { monaco: { language: 'python' } }
                    })
                ];

                for (let i = 0; i < tabs.length; i++) {
                    tabs[i].bind('data', async (tab) => {
                        editor.meta.info = await editor.tab(0).data();
                        let { code, data } = await wiz.call('read', { path: tab.path });
                        if (code != 200) data = null;
                        if (!data) {
                            if (tab.name == 'Component') {
                                data = DEFAULT_COMPONENT;
                            } else if (tab.name == 'API') {
                                data = DEFAULT_API;
                            }
                        }

                        return { data };
                    }).bind('update', async (tab) => {
                        let data = await tab.data();
                        await this.update(tab.path, data.data);
                    });
                }

                editor.bind("delete", async () => {
                    let res = await this.service.alert.show({ title: 'Delete App', message: 'Are you sure remove "' + editor.title + '"?', action_text: "Delete", action_class: "btn-danger" });
                    if (res !== true) return;

                    let targets = await this.service.editor.find(editor);
                    for (let i = 0; i < targets.length; i++)
                        await targets[i].close();

                    await this.delete(node, true);
                });

                editor.bind("clone", async (location: number = -1) => {
                    await this.open(node, location);
                });

                await editor.open(location);
            },
            route: async () => {
                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: node.path,
                    title: node.name,
                    unique: true,
                    current: 1
                });

                editor.create({
                    name: 'info',
                    viewref: RouteInfoEditor,
                    path: node.path + "/app.json"
                }).bind('data', async (tab) => {
                    let { code, data } = await wiz.call('read', { path: tab.path });
                    if (code != 200) return {};
                    editor.meta.id = JSON.parse(data).id;
                    data = JSON.parse(data);
                    return data;
                }).bind('update', async (tab) => {
                    let data = await tab.data();

                    let check = /^[a-z0-9.]+$/.test(data.id);
                    if (!check) return toastr.error("invalidate id");
                    if (data.id.length < 3) return toastr.error("id at least 3 alphabets");

                    let from = editor.meta.id;
                    let to = data.id;

                    // if moved
                    if (from != to) {
                        node.rename = to;
                        let res = await this.move(node);
                        if (!res) {
                            toastr.error("invalidate namespace");
                            return;
                        }
                    }

                    node.path = node.path.split("/")
                    node.path[2] = to;
                    node.path = node.path.join("/");

                    editor.modify({ path: node.path + to, title: data.title ? data.title : data.id, subtitle: data.route, meta: { id: to } });

                    for (let i = 0; i < editor.tabs.length; i++) {
                        let topath: any = editor.tabs[i].path + '';
                        topath = topath.split("/");
                        topath[2] = to;
                        topath = topath.join("/");
                        editor.tabs[i].move(topath);
                    }

                    data = JSON.stringify(data, null, 4);
                    await this.update(node.path + '/app.json', data, node);
                });

                editor.create({
                    name: 'Controller',
                    viewref: MonacoEditor,
                    path: node.path + "/controller.py",
                    config: { monaco: { language: 'python' } }
                }).bind('data', async (tab) => {
                    tab.meta.info = await editor.tab(0).data();
                    let { code, data } = await wiz.call('read', { path: tab.path });
                    if (code != 200) return {};
                    return { data };
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    await this.update(tab.path, data.data);
                });

                editor.bind("delete", async () => {
                    let res = await this.service.alert.show({ title: 'Delete Route', message: 'Are you sure remove "' + editor.title + '"?', action_text: "Delete", action_class: "btn-danger" });
                    if (res !== true) return;

                    let targets = await this.service.editor.find(editor);
                    for (let i = 0; i < targets.length; i++)
                        await targets[i].close();
                    await this.delete(node, true);
                });

                await editor.open();
            },
            default: async () => {
                let viewtypes: any = {
                    'ts': { viewref: MonacoEditor, config: { monaco: { language: 'typescript', renderValidationDecorations: 'off' } } },
                    'js': { viewref: MonacoEditor, config: { monaco: { language: 'javascript' } } },
                    'css': { viewref: MonacoEditor, config: { monaco: { language: 'css' } } },
                    'scss': { viewref: MonacoEditor, config: { monaco: { language: 'scss' } } },
                    'json': { viewref: MonacoEditor, config: { monaco: { language: 'json' } } },
                    'pug': { viewref: MonacoEditor, config: { monaco: { language: 'pug' } } },
                    'py': { viewref: MonacoEditor, config: { monaco: { language: 'python' } } }
                };

                let extension = node.path.substring(node.path.lastIndexOf(".") + 1).toLowerCase();

                if (!viewtypes[extension]) {
                    await this.download(node);
                    return;
                }

                let { viewref, config } = viewtypes[extension];

                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: node.path,
                    title: node.name,
                    unique: true,
                    current: 0
                });

                editor.create({
                    name: 'config',
                    viewref: viewref,
                    path: node.path,
                    config: config
                }).bind('data', async (tab) => {
                    let { code, data } = await wiz.call('read', { path: node.path });
                    if (code != 200) return {};
                    return { data };
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    await this.update(node.path, data.data);
                });

                await editor.open();
            }
        }

        if (openEditor[node.type]) await openEditor[node.type]()
        else await openEditor.default();
    }

    public async upload(node: FileNode | null, mode: string = 'file') {
        if (!node) node = this.rootNode;

        let fd = new FormData();

        let fn = (api: string, fd: any) => new Promise((resolve) => {
            let url = wiz.url(api);
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

        let files: any = null;

        if (mode == 'app') {
            files = await this.service.file.select({ accept: '.wizapp' });
        } else {
            files = await this.service.file.select();
        }

        let filepath = [];
        for (let i = 0; i < files.length; i++) {
            if (!files[i].filepath) files[i].filepath = files[i].name;
            fd.append('file[]', files[i]);
            filepath.push(files[i].filepath);
        }

        fd.append("filepath", JSON.stringify(filepath));
        fd.append("path", node.path);

        if (mode == 'app') {
            await fn('upload_app', fd);
        } else {
            await fn('upload', fd);
        }

        await this.refresh(node, false);
        await this.loader(false);
    }

    public async move(node: FileNode) {
        let { rename, path } = node;
        let name = path.split("/");
        name = name[name.length - 1];
        if (name == rename) {
            node.editable = false;
            return false;
        }

        let to: any = path.split("/");
        to[to.length - 1] = rename;
        to = to.join("/");
        let parent_path = to.split("/").slice(0, to.split("/").length - 1).join("/");

        let { code } = await wiz.call("move", { path, to });

        if (code !== 200) {
            toastr.error("Error on change path");
            return false;
        }

        node.parent = null;
        for (let i = 0; i < this.dataSource.data.length; i++) {
            if (this.dataSource.data[i].path == parent_path) {
                node.parent = this.dataSource.data[i];
                break;
            }
        }

        await this.dataSource.delete(node);
        await this.refresh(node);
        return true;
    }

    public async delete(node: FileNode, forced: boolean = false) {
        if (node.type != "new.folder" && node.type != "new.file") {
            if (!forced) {
                let res = await this.service.alert.show({ title: 'Delete', message: 'Are you sure to delete?', action_text: "Delete", action_class: "btn-danger" });
                if (!res) return;
            }
            await wiz.call("delete", { path: node.path });
        }
        await this.dataSource.delete(node);
    }

    public async create(node: FileNode | null, type: any) {
        if (!node) {
            return;
        }

        if (node.type == "new.folder" || node.type == "new.file") {
            let type = node.type.split(".")[1];
            let path = node.path + "/" + node.name;
            let { code } = await wiz.call("create", { type, path });

            if (code != 200) {
                toastr.error("invalid filename");
                return;
            }

            await this.dataSource.delete(node);
            await this.refresh(node);
        } else if (type == "mod.app") {
            let mode = node.type.split(".")[1];
            let editor = this.service.editor.create({ component_id: this.APP_ID, title: 'New' });

            editor.create({ name: 'info', viewref: node.type == 'mod.page' ? PageInfoEditor : AppInfoEditor })
                .bind('data', async () => {
                    return { mode: mode, id: '', title: '', namespace: '', viewuri: '', category: '' };
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.namespace);
                    if (!check) return toastr.error("invalidate namespace");
                    if (data.namespace.length < 3) return toastr.error("namespace at least 3 alphabets");

                    let id = mode + "." + data.namespace;
                    let app_namespace = data.namespace;
                    data.mode = mode;
                    data.id = id;
                    let res = await wiz.call("exists", { path: node.path + "." + app_namespace });
                    if (res.data) return toastr.error("namespace already exists");
                    data = JSON.stringify(data, null, 4);
                    editor.close();
                    await this.update(node.path + "." + app_namespace + '/app.json', data, node);
                });

            await editor.open();
        } else if (node.type == "mod.route") {
            let editor = this.service.editor.create({ component_id: this.APP_ID, title: 'New' });

            editor.create({ name: 'info', viewref: RouteInfoEditor })
                .bind('data', async () => {
                    return { id: '', title: '', route: '', viewuri: '', category: '' };
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.id);
                    if (!check) return toastr.error("invalidate id");
                    if (data.id.length < 3) return toastr.error("id at least 3 alphabets");
                    let res = await wiz.call("exists", { path: node.path + "/" + data.id });
                    if (res.data) return toastr.error("namespace already exists");

                    let appid = data.id;
                    data = JSON.stringify(data, null, 4);
                    editor.close();
                    await this.update(node.path + "/" + appid + '/app.json', data, node);
                });

            await editor.open();
        } else {
            if (!this.treeControl.isExpanded(node))
                await this.dataSource.toggle(node, true);
            let newitem = new FileNode('', node.path, 'new.' + type, node, node.level + 1);
            await this.dataSource.prepend(newitem, node);
        }
    }

    public async refresh(node: FileNode | null = null, isparent: boolean = true) {
        if (node) {
            if (isparent && node.parent) {
                await this.dataSource.toggle(node.parent, false);
                await this.dataSource.toggle(node.parent, true);
            } else {
                await this.dataSource.toggle(node, false);
                await this.dataSource.toggle(node, true);
            }
        } else {
            let data = await this.list(this.rootNode);
            this.dataSource.data = data;
        }
    }

    public async download(node: FileNode | null) {
        if (!node) node = this.rootNode;
        let target = wiz.url("download/" + node.path);
        window.open(target, '_blank');
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public async ngOnInit() {
        this.rootNode = new FileNode('root', this.path, 'folder');
        this.treeControl = new FlatTreeControl<FileNode>(this.getLevel, this.isExpandable);
        this.dataSource = new FileDataSource(this);
        let data = await this.list(this.rootNode);
        this.dataSource.data = data;
    }
}