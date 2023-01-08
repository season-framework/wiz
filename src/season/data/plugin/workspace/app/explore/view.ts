import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

import $ from 'jquery';
import toastr from "toastr";

import { FlatTreeControl } from '@angular/cdk/tree';
import { FileNode, FileDataSource, Workspace } from './service';

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

    constructor(private service: Service) {
        this.workspace = new Workspace(service, wiz);
    }

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

    private async update(path: string, data: string, node: any = null, viewuri: string | null = null) {
        let res = await wiz.call('update', { path: path, code: data });
        if (node) await this.refresh(node.parent);
        if (["route", "controller", "model", "config"].includes(path.split("/")[1])) {
            if (res.code == 200) toastr.info("Updated");
            return
        }

        if (res.code == 200) toastr.success("Updated");
        res = await wiz.call('build', { path: path });
        if (res.code == 200) toastr.info("Builded");
        else toastr.error("Error on build");

        let binding = this.service.event.load("workspace.app.preview");
        if (binding && viewuri) await binding.move(viewuri);
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
                await this.workspace.AppEditor(app).open(location);
            },
            route: async () => {
                let app = node.meta;
                await this.workspace.RouteEditor(app).open(location);
            },
            default: async () => {
                let path = node.path;
                let editor = this.workspace.FileEditor(path);
                if (editor) {
                    await editor.open(location);
                } else {
                    await this.download(node);
                }
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

        await this.refresh(node);
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
        await this.refresh(node.parent);
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
            await this.refresh(node.parent);
        } else if (type == "mod.app") {
            let mode = node.type.split(".")[1];
            let app = { mode: mode, id: '', title: '', namespace: '', viewuri: '', category: '' };
            await this.workspace.AppEditor(app).open();
        } else if (node.type == "mod.route") {
            let app = { id: '', title: '', route: '', viewuri: '', category: '' };
            await this.workspace.RouteEditor(app).open();
        } else {
            if (!this.treeControl.isExpanded(node))
                await this.dataSource.toggle(node, true);
            let newitem = new FileNode('', node.path, 'new.' + type, node, node.level + 1);
            await this.dataSource.prepend(newitem, node);
        }
    }

    public async refresh(node: FileNode | null = null) {
        if (node) {
            await this.dataSource.toggle(node, false);
            await this.dataSource.toggle(node, true);
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

    public find(path: string) {
        let data = this.dataSource.data;
        for (let i = 0; i < data.length; i++) {
            if (data[i].path == path)
                return data[i];
        }
        return null;
    }

    public async ngOnInit() {
        this.rootNode = new FileNode('root', this.path, 'folder');
        this.treeControl = new FlatTreeControl<FileNode>(this.getLevel, this.isExpandable);
        this.dataSource = new FileDataSource(this);
        let data = await this.list(this.rootNode);
        this.dataSource.data = data;

        this.service.event.bind(this.APP_ID, this);
    }
}