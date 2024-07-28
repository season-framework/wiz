import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import { Workspace } from './service';

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

    public getMod(path: string) {
        if (path.startsWith('src/angular')) return 'angular';
        if (path.startsWith('src/app/page')) return 'app/page';
        if (path.startsWith('src/app/component')) return 'app/component';
        if (path.startsWith('src/app/layout')) return 'app/layout';
        if (path.startsWith('src/angular/libs')) return 'libs';
        if (path.startsWith('src/angular/styles')) return 'styles';
        if (path.startsWith('src/assets')) return 'assets';
        if (path.startsWith('src/route')) return 'server/api';
        if (path.startsWith('src/model')) return 'server/model';
        if (path.startsWith('config')) return 'server/config';
        if (path.startsWith('src/reference')) return 'reference';
        return null;
    }

    public icon(node: any, checkopen: boolean = true) {
        if (node.type == 'app') return 'fa-solid fa-cube';
        if (node.type == 'route') return 'fa-solid fa-cube';
        if (node.id == 'src/angular') return 'text-red fa-brands fa-angular';
        if (node.id == 'src/app/page') return 'wiz-folder fa-solid fa-layer-group';
        if (node.id == 'src/app/component') return 'wiz-folder fa-solid fa-layer-group';
        if (node.id == 'src/app/layout') return 'wiz-folder fa-solid fa-layer-group';
        if (node.id == 'src/route') return 'wiz-folder fa-solid fa-link'
        if (node.id == 'src/angular/styles') return 'wiz-folder fa-brands fa-css3-alt';
        if (node.id == 'src/assets') return 'wiz-folder fa-solid fa-images';
        if (node.id == 'src/angular/libs') return 'wiz-folder fa-solid fa-book';
        if (node.id == 'src/reference') return 'wiz-folder fa-solid fa-book';
        if (node.type == 'folder') {
            if (node.isOpen() && checkopen) return 'wiz-folder fa-regular fa-folder-open';
            else return 'wiz-folder fa-solid fa-folder';
        }
        return 'fa-regular fa-file-lines';
    }

    public enableCreateFile(node: any) {
        if (node.type != 'folder') return false;
        if (node.root_id != 'src') {
            if (node.id.startsWith('src/app')) return false;
            if (node.id.startsWith('src/route')) return false;
        }
        return true;
    }

    public enableCreateFolder(node: any) {
        if (node.type != 'folder') return false;
        if (node.id.startsWith('src/app')) return false;
        if (node.id.startsWith('src/route')) return false;
        return true;
    }

    public enableUpload(node: any) {
        if (node.type != 'folder') return false;
        if (node.id.startsWith('src/route')) return false;
        if (node.root_id != 'src') {
            if (node.id.startsWith('src/app')) return false;
        }
        return true;
    }

    public enableDelete(node: any) {
        if (node.root_id != 'src') return true;
        return false;
    }

    public enableDownload(node: any) {
        if (node.id.startsWith("src/route")) return false;
        if (node.id == "src/app/page") return false;
        if (node.id == "src/app/component") return false;
        if (node.id == "src/app/layout") return false;
        return true;
    }

    public treeConfig: any = {
        ROOTKEY: 'src',
        load: async (path: any) => {
            let res = await wiz.call("tree", { path: path });
            return res;
        },
        sort: (key, children) => {
            if (!key) return;
            if (key == 'src') return;

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
                    if (targetpath.startsWith('src/app') || targetpath.startsWith('src/route')) {
                        if (targetpath.split("/")[2] == node.id.split("/")[2]) {
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
        if (node.root_id == 'src') return;
        event.stopPropagation();
        node.editable = !node.editable;
        await this.service.render();
    }

    public async open(node: any, location: number = -1) {
        if (!node) return;
        if (node.editable) return;
        if (node.type.split(".")[0] == "new") return;

        let openEditor = {
            app: async () => {
                let app = node.meta;
                await this.workspace.AppEditor(app).open(location);
            },
            route: async () => {
                let app = node.meta;
                await this.workspace.RouteEditor(app).open(location);
            },
            default: async () => {
                let path = node.id;
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

    public uploadStatus: any = {
        uploading: false,
        percent: 0
    };

    public async upload(node: any, files: any = null) {
        if (node.type == 'file')
            node = node.parent();
        if (node.id == 'src') return;
        let mode: any = this.getMod(node.id);

        if (!files)
            if (mode.startsWith('app')) {
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
        if (mode.startsWith('app'))
            url = wiz.url('upload_app');

        await this.service.file.upload(url, fd, this.uploadProgress.bind(this));
        await node.refresh();
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

    public async delete(node: any, forced: boolean = false) {
        if (!forced) {
            let res = await this.service.alert.show({ title: 'Delete', message: 'Are you sure to delete?', action_text: "Delete", action_class: "btn-danger" });
            if (!res) return;
        }
        await node.flush();
        await wiz.call("delete", { path: node.id });
        await node.parent().refresh();
    }

    public async createFile(node: any) {
        if (node.id.startsWith("src/app")) {
            let mode = node.id.split("/")[2];
            let app = { mode: mode, id: '', title: '', namespace: '', viewuri: '', category: '' };
            await this.workspace.AppEditor(app).open();
            return;
        }

        if (node.id.startsWith("src/route")) {
            let app = { id: '', title: '', route: '', viewuri: '', category: '' };
            await this.workspace.RouteEditor(app).open();
            return;
        }

        node.newItem = { type: 'file', root_id: node.id ? node.id : '' };
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
        await node.refresh();
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
        await node.refresh();
    }

    public async cancelCreate(node: any) {
        delete node.newItem;
        await this.service.render();
    }

    public async refresh(node: any = null) {
        if (!node) return;
        try {
            node = this.treeConfig.info(node.id);
            await node.refresh();
        } catch (e) {
        }
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