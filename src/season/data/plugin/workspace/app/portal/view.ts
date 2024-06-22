import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import { Workspace } from './service';

import ModuleInfoEditor from "@wiz/app/workspace.editor.portal.info";

export class Component implements OnInit {
    constructor(private service: Service) { this.workspace = new Workspace(service, wiz); }

    public APP_ID: string = wiz.namespace;
    public loading: boolean = false;
    public current: any;

    public async ngOnInit() {
        while (!this.treeConfig.rootNode)
            await this.service.render(100);
        this.current = this.treeConfig.rootNode();
        this.service.event.bind(this.APP_ID, this);
    }

    public getModName(path: string) {
        return path.split("/")[1];
    }

    public getMod(path: string, level: number = 0) {
        let segment: any = path.split('/');

        if (segment[2] == 'sample' && segment.length > 3) {
            let seg: any = segment[3].split(".");
            if (seg.length == 2) {
                segment[3] = seg[0];
                segment.push(seg[1]);
            }
        }

        if (segment.length == level) return segment[2];
        if (level === 0 && segment.length >= 3) return segment[2];
        return null;
    }

    public icon(node: any, checkopen: boolean = true) {
        if (node.root_id == 'portal') return 'fa-solid fa-rocket';
        if (['app', 'route', 'layout', 'component', 'page'].includes(node.type)) return 'fa-solid fa-cube';

        let mod: any = this.getMod(node.id, 3);
        if (mod == 'sample') return 'wiz-folder fa-solid fa-layer-group';
        if (mod == 'app') return 'wiz-folder fa-solid fa-layer-group';
        if (mod == 'widget') return 'wiz-folder fa-solid fa-layer-group';
        if (mod == 'route') return 'wiz-folder fa-solid fa-link';
        if (mod == 'libs') return 'wiz-folder fa-solid fa-book';
        if (mod == 'styles') return 'wiz-folder fa-brands fa-css3-alt';
        if (mod == 'assets') return 'wiz-folder fa-solid fa-images';
        if (mod == 'portal.json') return 'text-red fa-solid fa-circle-info';
        if (['sample'].includes(this.getMod(node.id, 4))) return 'wiz-folder fa-solid fa-tag';

        if (node.type == 'folder') {
            if (node.isOpen() && checkopen) return 'wiz-folder fa-regular fa-folder-open';
            else return 'wiz-folder fa-solid fa-folder';
        }

        return 'fa-regular fa-file-lines';
    }

    public isRoot(node: any) {
        if (node.root_id == 'portal') return true;
        return false;
    }

    public enableCreateFile(node: any) {
        if (node.root_id == 'portal') return false;
        if (node.type != 'folder') return false;
        if (['sample'].includes(this.getMod(node.id, 3))) return false;
        return true;
    }

    public enableCreateFolder(node: any) {
        if (node.root_id == 'portal') return false;
        if (node.type != 'folder') return false;
        if (['sample', 'app', 'widget', 'route'].includes(this.getMod(node.id, 3))) return false;
        if (['sample'].includes(this.getMod(node.id, 4))) return false;
        return true;
    }

    public enableUpload(node: any) {
        if (node.root_id == 'portal') return false;
        if (node.type != 'folder') return false;
        if (['sample', 'route'].includes(this.getMod(node.id))) return false;
        return true;
    }

    public enableDelete(node: any) {
        if (this.getMod(node.id, 3)) return false;
        if (['sample'].includes(this.getMod(node.id, 4))) return false;
        return true;
    }

    public enableInstall(node: any) {
        if (['sample'].includes(this.getMod(node.id, 5)))
            return true;
        return false;
    }

    public enableDownload(node: any) {
        if (['sample', 'app', 'widget', 'route'].includes(this.getMod(node.id, 3))) return false;
        if (['sample'].includes(this.getMod(node.id, 4))) return false;
        if (['sample'].includes(this.getMod(node.id, 5))) return false;
        if (['route'].includes(this.getMod(node.id, 4))) return false;
        return true;
    }

    public treeConfig: any = {
        ROOTKEY: 'portal',
        load: async (path: any) => {
            let res = await wiz.call("tree", { path: path });
            return res;
        },
        sort: (key, children) => {
            if (this.getMod(key, 3) == 'sample') return;
            if (!key) return;
            if (key == 'portal') return;
            if (key.split("/").length == 2) return;

            children.sort((a, b) => {
                if (a.type == b.type)
                    return a.title.localeCompare(b.title);
                if (a.type == 'folder') return -1;
                if (b.type == 'folder') return 1;
            });
        },
        select: async (node: any) => {
            if (node.type == 'folder') {
                if (node.id != this.current.id)
                    await node.toggle();
                return;
            }
            await this.open(node);
        },
        update: async (node: any) => {
            let { id, rename, root_id } = node;

            if (['sample', 'app', 'widget', 'route'].includes(this.getMod(node.id))) return false;
            let orgMod: string = this.getMod(id);
            let changeMod: string = this.getMod(root_id);

            if (!orgMod || !changeMod) return false;
            if (orgMod != changeMod) return false;

            if (id.startsWith(root_id) && id.split("/").length === root_id.split("/").length + 1) {
                let name = id.split("/");
                name = name[name.length - 1];
                if (name == rename) {
                    node.editable = false;
                    return;
                }
            }

            let to: any = root_id + '/' + rename;
            let { code } = await wiz.call("move", { path: id, to: to });
            if (code !== 200) {
                await this.service.alert.error("Error on change path");
                return false;
            }
        },
        upload: async (node: any, files: any) => {
            await this.upload(node, files);
        },
        isActive: (node: any) => {
            try {
                if (this.service.editor.activated) {
                    let targetpath = this.service.editor.activated.tab().path;
                    let mod: any = this.getMod(targetpath);
                    if (['sample', 'app', 'widget', 'route'].includes(mod)) {
                        if (targetpath.split("/")[3] == node.id.split("/")[3]) {
                            return true;
                        }
                    }

                    if (targetpath == node.id) {
                        return true;
                    }
                }
            } catch (e) {
            }
            return false;
        }
    }

    public drag(event: any, node: any) {
        event.dataTransfer.setData("text", node.meta.template);
    }

    public async rename(event: any, node: any) {
        let segment: any = node.id.split('/');
        if (segment.length <= 3) return;
        if (['sample', 'app', 'route', 'widget'].includes(segment[2])) return;
        event.stopPropagation();
        node.editable = !node.editable;
        await this.service.render();
    }

    private async update(path: string, data: string) {
        let res = await wiz.call('update', { path: path, code: data });
        let node: any = await this.treeConfig.info(path);
        await this.refresh(node.parent());

        await this.service.statusbar.process("build project...");
        res = await wiz.call('build', { path: path });
        if (res.code == 200) await this.service.statusbar.info("build finish", 5000);
        else await this.service.statusbar.error("error on build");
    }

    public async open(node: any, location: number = -1) {
        if (!node) return;
        if (node.editable) return;
        if (node.type.split(".")[0] == "new") return;

        let openEditor = {
            samplepage: async () => {
                let path = node.id.split("/");
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
                let path = node.id.split("/");
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
                let path = node.id.split("/");
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
                let path = node.id.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                let editor = await this.workspace.AppEditor(mod_id, app);
                await editor.open(location);
            },
            widget: async () => {
                let path = node.id.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                app.namespace = app_id;
                let editor = await this.workspace.AppEditor(mod_id, app);
                await editor.open(location);
            },
            route: async () => {
                let path = node.id.split("/");
                let mod_id = path[1];
                let app_id = path[path.length - 1];
                let app = node.meta;
                app.id = app_id;
                let editor = await this.workspace.RouteEditor(mod_id, app);
                await editor.open(location);
            },
            info: async () => {
                let path = node.id.split("/");
                let app_package = path[path.length - 2];

                let editor = this.service.editor.create({
                    component_id: this.APP_ID,
                    path: node.id,
                    title: app_package,
                    unique: true,
                    current: 0
                });

                editor.create({
                    name: 'info',
                    viewref: ModuleInfoEditor,
                    path: node.id
                }).bind('data', async () => {
                    let { code, data } = await wiz.call('read', { path: node.id });
                    if (code != 200) return { package: app_package };
                    data = JSON.parse(data);
                    data.package = app_package;
                    return data;
                }).bind('update', async (tab) => {
                    let data = await tab.data();
                    let check = /^[a-z0-9.]+$/.test(data.package);
                    if (!check) return this.service.alert.error("invalidate package name");
                    if (data.package.length < 3) return this.service.alert.error("package name at least 3 alphabets");
                    await this.update(node.id, JSON.stringify(data, null, 4));
                });

                await editor.open(location);
            },
            default: async () => {
                let editor = await this.workspace.FileEditor(node.id);
                if (editor) {
                    await editor.open(location);
                } else {
                    await this.download(node);
                }
            }
        }

        if (node.id.split("/")[2] == 'sample') {
            if (openEditor["sample" + node.type]) return await openEditor["sample" + node.type]();
        } else {
            if (openEditor[node.type]) return await openEditor[node.type]();
            if (node.meta && openEditor[node.meta.editor]) return await openEditor[node.meta.editor]();
            await openEditor.default();
        }
    }

    public uploadStatus: any = {
        uploading: false,
        percent: 0
    };

    public async upload(node: any, files: any = null) {
        if (node.type == 'file') node = node.parent();
        let mode: any = this.getMod(node.id);

        if (['sample', 'route'].includes(mode)) return;

        if (!files)
            if (node.id == 'portal') {
                files = await this.service.file.select({ accept: '.wizportal' });
            } else if (['app', 'widget'].includes(mode)) {
                files = await this.service.file.select({ accept: '.wizapp' });
            } else {
                files = await this.service.file.select();
            }

        let fd = new FormData();
        let filepath = [];
        for (let i = 0; i < files.length; i++) {
            if (!files[i].filepath) files[i].filepath = files[i].name;
            filepath.push(files[i].filepath);
            fd.append('file[]', files[i]);
        }
        fd.append('filepath', JSON.stringify(filepath));
        fd.append("path", node.id);

        let url: any = wiz.url('upload');
        if (['app', 'widget'].includes(mode)) url = wiz.url('upload_app');
        if (node.id == 'portal') url = wiz.url('upload_root');

        await this.service.file.upload(url, fd, this.uploadProgress.bind(this));
        await this.refresh(node);
    }

    public async uploadProgress(percent: number, total: number, position: number) {
        if (percent == 0) {
            this.uploadStatus.uploading = false;
            this.uploadStatus.percent = 0;
        } else if (percent == 100) {
            this.uploadStatus.uploading = false;
            this.uploadStatus.percent = 0;
        } else {
            this.uploadStatus.uploading = true;
            this.uploadStatus.percent = percent;
        }
        await this.service.render();
    }

    public async download(node: any) {
        if (!node) node = this.treeConfig.rootNode();
        let target = wiz.url("download/" + node.id);
        window.open(target, '_blank');
    }

    public async install(node: any) {
        let res = await this.service.alert.show({ title: 'Install', message: 'Are you sure to install `' + node.title + '`?', action: "Install", actionBtn: "success", status: 'success' });
        if (!res) return;
        let { code } = await wiz.call("install_sample", { path: node.id });
        if (code == 200) this.service.statusbar.info("Installed", 5000);
        else this.service.alert.error("Already Installed");
    }

    public async delete(node: any, forced: boolean = false) {
        if (!forced) {
            let res = await this.service.alert.show({ title: 'Delete', message: 'Are you sure to delete?', action_text: "Delete", action_class: "btn-danger" });
            if (!res) return;
        }
        await node.flush();
        await wiz.call("delete", { path: node.id });
        await this.refresh(node.parent());
    }

    public async createFile(node: any) {
        let mod: any = this.getMod(node.id);

        if (mod == 'app' || mod == 'widget') {
            let mod_id = this.getModName(node.id);
            let editor = await this.workspace.AppEditor(mod_id, { type: mod, mode: 'portal', title: '', id: '', namespace: mod == 'app' ? '' : 'widget.', viewuri: '', category: '' });
            await editor.open();
        } else if (mod == 'route') {
            let mod_id = this.getModName(node.id);
            let editor = await this.workspace.RouteEditor(mod_id, { id: '', title: '', route: '', viewuri: '', category: '' });
            await editor.open();
        } else if (mod == 'sample') {
            let submod: any = node.id.split("/")[3];
            if (submod == 'page') {
                let mod_id = this.getModName(node.id);
                let editor = await this.workspace.PageEditor(mod_id, { mode: 'sample', id: '', title: '', namespace: submod + '.', viewuri: '', category: '' });
                await editor.open();
            } else {
                let mod_id = this.getModName(node.id);
                let editor = await this.workspace.AppEditor(mod_id, { mode: 'sample', id: '', title: '', namespace: submod + '.', viewuri: '', category: '' });
                await editor.open();
            }
        } else {
            node.newItem = { type: 'file', root_id: node.id ? node.id : '' };
        }

        await this.service.render();
    }

    public async requestCreateFile(node: any) {
        let data: any = null;
        data = JSON.parse(JSON.stringify(node.newItem));

        let type = 'file';
        let path = node.id + "/" + data.title;

        let { code } = await wiz.call("create", { type, path });

        if (code != 200) {
            await this.service.alert.error("invalid filename");
            return;
        }

        delete node.newItem;
        await this.refresh(node);
    }

    public async createFolder(node: any) {
        node.newItem = { type: 'folder', root_id: node.id ? node.id : '' };
        await this.service.render();
    }

    public async requestCreateFolder(node: any) {
        let data: any = null;
        data = JSON.parse(JSON.stringify(node.newItem));

        let type = 'folder';
        let path = node.id + "/" + data.title;

        let { code } = await wiz.call("create", { type, path });

        if (code != 200) {
            await this.service.alert.error("invalid filename");
            return;
        }

        delete node.newItem;
        await this.refresh(node);
    }

    public async cancelCreate(node: any) {
        delete node.newItem;
        await this.service.render();
    }

    public async refresh(node: any = null) {
        if (!node) node = this.treeConfig.rootNode();
        else node = this.treeConfig.info(node.id);
        if (!node) node = this.treeConfig.rootNode();
        await node.refresh();
        await this.service.render();
    }

    public find(path: string) {
        try {
            let data: any = this.treeConfig.info(path);
            let res: any = JSON.parse(JSON.stringify(data));
            res.path = data.id;
            res.parent = data.parent();
            return res;
        } catch (e) {
        }
        return null;
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }
}