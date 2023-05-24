import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

import $ from 'jquery';

import { FlatTreeControl } from '@angular/cdk/tree';
import { FileNode, FileDataSource, Workspace } from './service';

import ModuleInfoEditor from "@wiz/app/workspace.editor.portal.info";

@dependencies({
    MatTreeModule: '@angular/material/tree'
})
export class Component implements OnInit {
    public path: string = 'portal';

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
    public isRoot = (node: FileNode) => node.path.split("/").length == 2;

    constructor(private service: Service) {
        this.workspace = new Workspace(service, wiz);
    }

    public async upgrade(node: any) {
        let res = await this.service.alert.show({ title: 'Upgrade Package', message: 'Are you sure upgrade "' + node.name + '"?', action: "Upgrade", actionBtn: "success", status: "success" });
        if (res !== true) return;
        await this.loader(true);
        let path = node.path;
        await wiz.call('upgrade', { path });
        await this.loader(false);
        await this.refresh();
    }

    public drag(event: any, node: any) {
        event.dataTransfer.setData("text", node.meta.template);
    }

    public active(node: FileNode | null) {
        if (node.parent == this.rootNode) {
            return 'root-item p-0 pr-2 pl-2';
        }

        try {
            if (this.service.editor.activated) {
                let targetpath = this.service.editor.activated.tab().path;
                let splited = targetpath.split("/");
                if (splited.length > 2)
                    if (['app', 'route', 'widget'].includes(splited[2]))
                        if (targetpath.split("/")[2] == node.path.split("/")[2] && targetpath.split("/")[3] == node.path.split("/")[3])
                            return 'active';
                if (targetpath == node.path) {
                    return 'active';
                }
            }
        } catch (e) {
        }
        return '';
    }

    public async list(node: FileNode) {
        let { code, data } = await wiz.call("list", { path: node.path });
        data = data.map(item => new FileNode(item.name, item.path, item.type, node, node.level + 1, item.meta ? item.meta : {}));
        data.sort((a, b) => {
            if (a.type == b.type)
                return a.name.localeCompare(b.name);
            if (a.type == 'folder') return -1;
            if (b.type == 'folder') return 1;
        });
        return data;
    }

    private async update(path: string, data: string) {
        let res = await wiz.call('update', { path: path, code: data });
        await this.service.statusbar.warning("build project...");
        res = await wiz.call('build', { path: path });
        if (res.code == 200) await this.service.statusbar.info("build finish", 5000);
        else await this.service.statusbar.error("error on build");
    }

    public async build() {
        await this.service.statusbar.warning("build project...");
        let res = await wiz.call('build', {});
        if (res.code == 200) await this.service.statusbar.info("build finish", 5000);
        else await this.service.statusbar.error("error on build");
    }

    public async open(node: FileNode, location: number = -1) {
        if (!node) return;
        if (node.editable) return;
        if (node.type.split(".")[0] == "new") return;

        let openEditor = {
            samplepage: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                app.mode = 'sample';
                let editor = await this.workspace.PageEditor(mod_id, app);
                editor.ctrls = [];
                editor.layout = [];
                await editor.open(location);
            },
            samplecomponent: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                app.mode = 'sample';
                let editor = await this.workspace.AppEditor(mod_id, app);
                editor.ctrls = [];
                editor.layout = [];
                await editor.open(location);
            },
            samplelayout: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                app.mode = 'sample';
                let editor = await this.workspace.AppEditor(mod_id, app);
                editor.ctrls = [];
                editor.layout = [];
                await editor.open(location);
            },
            app: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                let editor = await this.workspace.AppEditor(mod_id, app);
                await editor.open(location);
            },
            widget: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                let editor = await this.workspace.AppEditor(mod_id, app);
                await editor.open(location);
            },
            route: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                let editor = await this.workspace.RouteEditor(mod_id, app);
                await editor.open(location);
            },
            info: async () => {
                let path = node.path.split("/");
                let app_package = path[path.length - 2];

                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: node.path,
                    title: app_package,
                    unique: true,
                    current: 0
                });

                editor.create({
                    name: 'info',
                    viewref: ModuleInfoEditor,
                    path: node.path
                }).bind('data', async () => {
                    let { code, data } = await wiz.call('read', { path: node.path });
                    if (code != 200) return { package: app_package };
                    data = JSON.parse(data);
                    data.package = app_package;
                    return data;
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.package);
                    if (!check) return this.service.alert.error("invalidate package name");
                    if (data.package.length < 3) return this.service.alert.error("package name at least 3 alphabets");
                    await this.update(node.path, JSON.stringify(data, null, 4));
                });

                await editor.open(location);
            },
            default: async () => {
                let editor = await this.workspace.FileEditor(node.path);
                if (editor) {
                    await editor.open(location);
                } else {
                    await this.download(node);
                }
            }
        }

        if (node.path.split("/")[2] == 'sample') {
            if (openEditor["sample" + node.type]) return await openEditor["sample" + node.type]();
        } else {
            if (openEditor[node.type]) return await openEditor[node.type]();
            if (node.meta && openEditor[node.meta.editor]) return await openEditor[node.meta.editor]();
            await openEditor.default();
        }
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
        } else if (mode == 'root') {
            files = await this.service.file.select({ accept: '.wizportal' });
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
        } else if (mode == 'root') {
            await fn('upload_root', fd);
        } else {
            await fn('upload', fd);
        }

        await this.loader(false);
        await this.refresh(this.rootNode == node ? null : node);
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
            this.service.alert.error("Error on change path");
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
        await this.build();
    }

    public async create(node: FileNode | null, type: any) {
        if (!node) {
            let newitem = new FileNode('', this.rootNode.path, 'new.' + type, null, 0);
            await this.dataSource.prepend(newitem, null);
            return;
        }

        if (node.type == "new.folder" || node.type == "new.file") {
            let type = node.type.split(".")[1];
            let path = node.path + "/" + node.name;
            let { code } = await wiz.call("create", { type, path });

            if (code != 200) {
                this.service.alert.error("invalid filename");
                return;
            }

            await this.dataSource.delete(node);
            await this.refresh(node.parent);
        } else if (node.type == "mod.sample.page") {
            let path = node.path.split("/");
            let mod_id = path[1];
            let editor = await this.workspace.PageEditor(mod_id, { mode: 'sample', id: '', title: '', namespace: '', viewuri: '', category: '' });
            editor.ctrls = [];
            editor.layout = [];
            await editor.open();
        } else if (node.type == "mod.sample.app") {
            let path = node.path.split("/");
            let mod_id = path[1];
            let editor = await this.workspace.AppEditor(mod_id, { mode: 'sample', id: '', title: '', namespace: '', viewuri: '', category: '' });
            editor.ctrls = [];
            editor.layout = [];
            await editor.open();
        } else if (node.type == "mod.sample") {
            let path = node.path.split("/");
            let mod_id = path[1];
            let editor = await this.workspace.AppEditor(mod_id, { mode: 'sample', id: '', title: '', namespace: '', viewuri: '', category: '' });
            editor.ctrls = [];
            editor.layout = [];
            await editor.open();
        } else if (node.type == "mod.app") {
            let path = node.path.split("/");
            let mod_id = path[1];
            let editor = await this.workspace.AppEditor(mod_id, { mode: 'portal', id: '', title: '', namespace: '', viewuri: '', category: '' });
            await editor.open();
        } else if (node.type == "mod.route") {
            let path = node.path.split("/");
            let mod_id = path[1];
            let editor = await this.workspace.RouteEditor(mod_id, { id: '', title: '', route: '', viewuri: '', category: '' });
            await editor.open();
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

    public async downloadApp(node: FileNode | null) {
        let app = wiz.app("workspace.editor.ngapp.info")
        let target = app.url("download/" + node.path)
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

    public async install(node: FileNode) {
        let res = await this.service.alert.show({ title: 'Install', message: 'Are you sure to install `' + node.name + '`?', action: "Install", actionBtn: "success", status: 'success' });
        if (!res) return;
        let { code } = await wiz.call("install_sample", { path: node.path });
        if (code == 200) this.service.statusbar.info("Installed", 5000);
        else this.service.alert.error("Already Installed");
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