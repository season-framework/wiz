import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

import { DEFAULT_GITIGNORE } from "./service";

import MonacoEditor from "@wiz/app/core.editor.monaco";
import WorkspaceInfo from "@wiz/app/workspace.editor.wsinfo";

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public current: string = wiz.project();
    public keyword: string = "";
    public loading: boolean = false;
    public isCreate: boolean = false;
    public data: any = [];
    public info: any = { id: "" };
    public isdev = wiz.dev();

    constructor(private service: Service) { }

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

    public validate(info: any) {
        let list = [];
        for (let i = 0; i < this.data.length; i++)
            list.push(this.data[i].id);

        if (!info.id || !this.validateId(info.id))
            return "Only lowercase alphabetic characters are allowed for the project name.";

        if (info.type == 'copy') {
            if (!info.target) return "Select target";
            if (!list.includes(info.target)) return "Select target";
        }

        if (info.type == 'git') {
            if (!info.git) return "git repo is empty";
        }

        return true;
    }

    public validateId(name: string) {
        for (let i = 0; i < this.data.length; i++)
            if (name == this.data[i].id)
                return false;
        if (name.length < 3)
            return false;
        if (/^[a-z0-9]+$/.test(name))
            return true;
        return false;
    }

    public async onCreate() {
        this.info = { id: "", type: "sample", target: "" };
        if (this.keyword)
            this.info.id = this.keyword;

        if (this.data.length == 0) {
            this.info.id = "main";
            this.info.idDisabled = true;
        }

        this.isCreate = true;
        await this.service.render();
    }

    public async onCancelCreate() {
        this.isCreate = false;
        await this.service.render();
    }

    public async create() {
        let check = this.validate(this.info);
        if (check !== true)
            return await this.service.alert.error(check);

        if (this.info.type == 'upload') {
            let files = await this.service.file.select({ accept: ".wizproject", multiple: false });
            await this.service.loading.show();

            try {
                let fd = new FormData();
                for (let i = 0; i < files.length; i++) {
                    if (!files[i].filepath) files[i].filepath = files[i].name;
                    fd.append('file[]', files[i]);
                }
                fd.append("path", this.info.id);
                fd.append("type", "upload");

                let url = wiz.url('create');
                let { code } = await this.service.file.upload(url, fd);
                if (code !== 200) {
                    await this.service.alert.error("Already exists project");
                    await this.service.loading.hide();
                    return;
                }
            } catch (e) {
            }
        } else {
            await this.service.loading.show();

            try {
                let { code } = await wiz.call("create", { path: this.info.id, ...this.info });
                if (code !== 200) {
                    await this.service.alert.error("Already exists project");
                    await this.service.loading.hide();
                    return;
                }
            } catch (e) {
            }
        }

        this.keyword = "";
        this.isCreate = false;
        await this.service.loading.hide();
        await this.load();
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
                this.service.statusbar.info("updated", 5000);
            });
        }

        createTab(path + '/.git/config', 'conf', 'git/config', "");
        createTab(path + '/.gitignore', 'conf', 'git/ignore', DEFAULT_GITIGNORE);

        await editor.open();
    }
}