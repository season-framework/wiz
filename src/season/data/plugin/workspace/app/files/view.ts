import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

import $ from 'jquery';
import toastr from "toastr";

import { FlatTreeControl } from '@angular/cdk/tree';
import { FileNode, FileDataSource } from './service';

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
    @Input() title: string = "Files";
    @Input() path: string;
    
    public color = '';

    public APP_ID: string = wiz.namespace;
    public loading: boolean = false;
    public rootNode: FileNode;

    private treeControl: FlatTreeControl<FileNode>;
    private dataSource: FileDataSource;
    private getLevel = (node: FileNode) => node.level;
    private isExpandable = (node: FileNode) => node.extended;
    private isFolder = (_: number, node: FileNode) => node.type == 'folder';
    private isNew = (_: number, node: FileNode) => node.type == 'new.folder' || node.type == 'new.file';

    constructor(private service: Service) {
    }

    public active(node: FileNode | null) {
        try {
            if (this.service.editor.activated) {
                if (this.service.editor.activated.tab().path == node.path) {
                    return true;
                }
            }
        } catch (e) {
        }
        return false;
    }

    public async list(node: FileNode) {
        let { code, data } = await wiz.call("list", { path: node.path });
        data = data.map(item => new FileNode(item.name, item.path, item.type, node, node.level + 1));
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
        if (res.code == 200) toastr.success("Updated");
    }

    public async open(node: FileNode) {
        if (!node) return;
        if (node.editable) return;
        if (node.type.split(".")[0] == "new") return;

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

    public upload_target: FileNode | null;
    public upload_mode: string = 'file';

    public async upload_file() {
        await this.loader(true);
        let target = this.upload_target;
        if (!target) target = this.rootNode;

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
        fd.append("path", target.path);
        await fn(fd);

        this.upload_target = null;
        await this.loader(false);
        await this.refresh(this.rootNode == target ? null : target);
    }

    public async upload(node: FileNode | null, mode: string = 'file') {
        this.upload_target = node;
        this.upload_mode = mode;
        await this.service.render();
        $('#file-upload').click();
    }

    public async move(node: FileNode) {
        let { name, rename, path } = node;
        if (name == rename) {
            node.editable = false;
            return;
        }

        let to: any = path.split("/");
        to[to.length - 1] = rename;
        to = to.join("/");
        let parent_path = to.split("/").slice(0, to.split("/").length - 1).join("/");

        let { code } = await wiz.call("move", { path, to });

        if (code !== 200) {
            toastr.error("Error on change path");
            return;
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
    }

    public async delete(node: FileNode) {
        if (node.type != "new.folder" && node.type != "new.file") {
            let res = await this.service.alert.show({ title: 'Delete', message: 'Are you sure to delete?', action_text: "Delete", action_class: "btn-danger" });
            if (!res) return;
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
                toastr.error("invalid filename");
                return;
            }

            await this.dataSource.delete(node);
            await this.refresh(node);
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