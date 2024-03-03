import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

import $ from 'jquery';

import { FlatTreeControl } from '@angular/cdk/tree';
import { FileNode, FileDataSource } from './service';

import MonacoEditor from "@wiz/app/core.editor.monaco";
import InfoEditor from "@wiz/app/core.editor.ide";
import PluginInfoEditor from "@wiz/app/core.editor.plugin.info";
import ImageViewer from "src/app/workspace.editor.image/workspace.editor.image.component";
import ReadmeViewer from "src/app/workspace.editor.readme/workspace.editor.readme.component";

const DEFAULT_COMPONENT = `import { OnInit, Input } from '@angular/core';

export class Replacement implements OnInit {
    @Input() title: any;

    public async ngOnInit() {
    }
}`.replace('Replacement', 'Component');

const DEFAULT_API = ``;

@dependencies({
    MatTreeModule: '@angular/material/tree'
})
export class Component implements OnInit {
    public path: string = 'plugin';

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

    constructor(private service: Service) { }

    public drag(event: any, node: any) {
        event.dataTransfer.setData("text", node.meta.template);
    }

    public active(node: FileNode | null) {
        try {
            if (this.service.editor.activated) {
                let targetpath = this.service.editor.activated.tab().path;
                let splited = targetpath.split("/");
                if (splited.length > 2)
                    if (splited[2] == 'app' || splited[2] == 'route')
                        if (targetpath.split("/")[2] == node.path.split("/")[2] && targetpath.split("/")[3] == node.path.split("/")[3])
                            return true;
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
            if (a.type == b.type)
                return a.path.localeCompare(b.path);
            if (a.type == 'folder') return -1;
            if (b.type == 'folder') return 1;
        });
        return data;
    }

    private async update(path: string, data: string) {
        let res = await wiz.call('update', { path: path, code: data });
        await this.service.statusbar.process("build project...");
        res = await wiz.call('build');
        if (res.code == 200) await this.service.statusbar.info("build finish", 5000);
        else await this.service.statusbar.error("error on build");
    }

    public async open(node: FileNode, location: number = -1) {
        if (!node) return;
        if (node.editable) return;
        if (node.type.split(".")[0] == "new") return;

        let openEditor = {
            app: async () => {
                let path = node.path.split("/");
                let mod_id = path[1];
                let mod_type = path[2];
                let app_id = path[path.length - 1];
                let namespace = mod_id + "." + mod_type + "." + app_id;

                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: node.path,
                    title: node.name,
                    subtitle: namespace,
                    current: 1
                });

                editor.namespace_prefix = mod_id + "." + mod_type + ".";

                editor.create({
                    name: 'info',
                    viewref: InfoEditor,
                    path: node.path + "/app.json"
                }).bind('data', async (tab) => {
                    let { code, data } = await wiz.call('read', { path: tab.path });
                    if (code != 200) return { mod_id, mod_type };
                    data = JSON.parse(data);
                    data.id = app_id;
                    data.mod_id = mod_id;
                    data.mod_type = mod_type;
                    return data;
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.id);
                    if (!check) return await this.service.alert.error("invalidate namespace");
                    if (data.id.length < 3) return await this.service.alert.error("namespace at least 3 alphabets");

                    let from = app_id;
                    let to = data.id;

                    if (from != to) {
                        node.rename = to;
                        let res = await this.move(node);
                        if (!res) {
                            await this.service.alert.error("invalidate namespace");
                            return;
                        }
                    }

                    app_id = data.id;

                    node.path = node.path.split("/")
                    node.path[3] = to;
                    node.path = node.path.join("/");

                    data.id = to;
                    editor.modify({ path: 'app/' + to, title: data.title ? data.title : data.namespace, subtitle: to });

                    for (let i = 0; i < editor.tabs.length; i++) {
                        let topath: any = editor.tabs[i].path + '';
                        topath = topath.split("/");
                        topath[3] = to;
                        topath = topath.join("/");
                        editor.tabs[i].move(topath);
                    }

                    node.name = data.title;
                    data = JSON.stringify(data, null, 4);
                    await this.update(node.path + '/app.json', data);
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
                        name: 'Service',
                        viewref: MonacoEditor,
                        path: node.path + "/service.ts",
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
                        if (code != 200) return {};

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
                    let res = await this.service.alert.show({ title: 'Delete App', message: 'Are you sure remove "' + editor.title + '"?', action: "Delete", actionBtn: "btn-danger" });
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
                    viewref: PluginInfoEditor,
                    path: node.path
                }).bind('data', async () => {
                    let { code, data } = await wiz.call('read', { path: node.path });
                    if (code != 200) return {};
                    data = JSON.parse(data);
                    return data;
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.package);
                    if (!check) return await this.service.alert.error("invalidate package name");
                    if (data.package.length < 3) return await this.service.alert.error("package name at least 3 alphabets");
                    await this.update(node.path, JSON.stringify(data, null, 4));
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
                        let { code, data } = await wiz.call('read', { path: tab.path });
                        if (code != 200) return {};
                        if (!data) data = dvalue;
                        return { data };
                    }).bind('update', async (tab) => {
                        let data = await tab.data();
                        await this.update(path, data.data);
                    });
                }

                createTab('plugin/workspace/filter.py', 'python', 'Filter', "");
                createTab('plugin/workspace/command.py', 'python', 'Command', "");
                createTab('plugin/workspace/shortcut.ts', 'typescript', 'Shortcut', "");

                await editor.open(location);
            },
            default: async () => {
                let viewtypes: any = {
                    'md': { viewref: MonacoEditor, config: { monaco: { language: 'markdown' } } },
                    'ts': { viewref: MonacoEditor, config: { monaco: { language: 'typescript', renderValidationDecorations: 'off' } } },
                    'js': { viewref: MonacoEditor, config: { monaco: { language: 'javascript' } } },
                    'css': { viewref: MonacoEditor, config: { monaco: { language: 'css' } } },
                    'scss': { viewref: MonacoEditor, config: { monaco: { language: 'scss' } } },
                    'json': { viewref: MonacoEditor, config: { monaco: { language: 'json' } } },
                    'pug': { viewref: MonacoEditor, config: { monaco: { language: 'pug' } } },
                    'py': { viewref: MonacoEditor, config: { monaco: { language: 'python' } } }
                };

                let extension = node.path.substring(node.path.lastIndexOf(".") + 1).toLowerCase();
                const imgExt = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg', 'ico'];
                const IS_IMG = imgExt.includes(extension);
                if (IS_IMG)
                    viewtypes[extension] = { viewref: ImageViewer, config: {} };

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

                if (extension == 'md') {
                    editor.create({
                        name: 'viewer',
                        viewref: ReadmeViewer,
                        path: node.path
                    }).bind('data', async (tab) => {
                        let { code, data } = await wiz.call('read', { path: node.path });
                        if (code != 200) return {};
                        return { data };
                    });
                }

                editor.create({
                    name: 'editor',
                    viewref: viewref,
                    path: node.path,
                    config: config
                }).bind('data', async (tab) => {
                    if (IS_IMG) return { data: node.path };
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

        if (openEditor[node.type]) return await openEditor[node.type]();
        if (node.meta && openEditor[node.meta.editor]) return await openEditor[node.meta.editor]();
        await openEditor.default();
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
            files = await this.service.file.select({ accept: '.wizplugapp' });
        } else if (mode == 'root') {
            files = await this.service.file.select({ accept: '.wizplug' });
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

            let build = async () => {
                await this.service.statusbar.process("build project...");
                let res = await wiz.call('build');
                if (res.code == 200) await this.service.statusbar.info("build finish", 5000);
                else await this.service.statusbar.error("error on build");
            }
            build();
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
            await this.service.alert.error("Error on change path");
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
                let res = await this.service.alert.show({ title: 'Delete', message: 'Are you sure to delete?', action: "Delete", actionBtn: "btn-danger" });
                if (!res) return;
            }
            await wiz.call("delete", { path: node.path });
        }
        await this.dataSource.delete(node);
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
                await this.service.alert.error("invalid filename");
                return;
            }

            await this.dataSource.delete(node);
            await this.refresh(node);
        } else if (node.type == "mod.app") {
            let editor = this.service.editor.create({ component_id: this.APP_ID, title: 'New' });

            editor.create({ name: 'info', viewref: InfoEditor })
                .bind('data', async () => {
                    return { id: '', title: '', category: '' };
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.id);
                    if (!check) return await this.service.alert.error("invalidate namespace");
                    if (data.id.length < 3) return await this.service.alert.error("namespace at least 3 alphabets");

                    let id = data.id;
                    let res = await wiz.call("exists", { path: node.path + "/" + id });
                    if (res.data) return await this.service.alert.error("namespace already exists");

                    let appid = id;
                    data.id = id;
                    data = JSON.stringify(data, null, 4);

                    editor.close();
                    await this.update(node.path + "/" + appid + '/app.json', data);
                });

            await editor.open();
        } else {
            if (!this.treeControl.isExpanded(node))
                await this.dataSource.toggle(node, true);
            let newitem = new FileNode('', node.path, 'new.' + type, node, node.level + 1);
            await this.dataSource.prepend(newitem, node);
        }
    }

    public async refresh(node: FileNode | null = null) {
        if (node && node.parent) {
            await this.dataSource.toggle(node.parent, false);
            await this.dataSource.toggle(node.parent, true);
        } else {
            let data = await this.list(this.rootNode);
            this.dataSource.data = data;
        }
    }

    public async upgrade(node: FileNode) {
        if (!node.meta.package) return;
        let res = await this.service.alert.show({ title: 'Upgrade Plugin', message: 'Are you sure upgrade "' + node.name + '"?', action: "Upgrade", actionBtn: "success", status: "success" });
        if (res !== true) return;
        await this.loader(true);
        await wiz.call("upgrade", { plugin: node.meta.package });
        await wiz.call('build');
        await this.loader(false);
    }

    public async coreUpgrade() {
        let res = await this.service.alert.show({ title: 'Upgrade Plugin', message: 'Are you sure upgrade?', action: "Upgrade", actionBtn: "success", status: "success" });
        if (res !== true) return;
        await this.loader(true);
        await wiz.call("coreupgrade");
        await wiz.call("upgrade", { plugin: 'core' });
        await wiz.call("upgrade", { plugin: 'git' });
        await wiz.call("upgrade", { plugin: 'utility' });
        await wiz.call("upgrade", { plugin: 'workspace' });
        await wiz.call('build');
        await this.loader(false);
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