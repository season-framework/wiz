import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import { Workspace } from 'src/app/workspace.app.explore/service';
import PortalWorkspace from 'src/app/workspace.app.portal/service';

export class Component implements OnInit {
    public loading: boolean = false;
    public list = [];
    public text: string = "";

    constructor(public service: Service) {
        this.workspace = new Workspace(service, wiz);
        this.portalWorkspace = new PortalWorkspace(service, wiz);
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public async ngOnInit() { }

    public async search() {
        const len = this.text.replace(/\s/g, "").length;
        if (len < 4) return await this.service.alert.show({ title: "Alert", message: "4글자 이상 검색해주세요.", cancel: false, action: "close" });
        
        this.list = [];
        await this.loader(true);
        const body = {
            text: this.text,
        };
        const targets = ["src", "portal", "config"];
        for (let i = 0; i < targets.length; i++) {
            const root = targets[i];
            body.root = root;
            const { code, data } = await wiz.call("search", body);
            if (code !== 200) continue;
            this.list.push(...data);
        }
        await this.loader(false);
    }

    public iconMap(root) {
        switch (root) {
            case "src": return `fa-folder-tree`;
            case "portal": return `fa-layer-group`;
            default: return ``;
        }
    }

    public async load(file) {
        let path = `${file.root}/${file.filepath}`;
        if (file.component) path = `${file.root}/${file.component}`;
        const { code, data } = await wiz.call("load", { path });
        if (code !== 200) return;
        const _type = data.type;
        const _data = data.data;
        let editor = null;
        if (_type === "app") {
            if (_data.mode === "portal") {
                const mod_id = _data["ng.build"].id.split(".")[1];
                editor = await this.portalWorkspace.AppEditor(mod_id, _data);
            }
            else editor = this.workspace.AppEditor(_data);
        }
        else if (_type === "file") {
            let force = false;
            try {
                const ext = this.list[this.idx].split(".").slice(-1)[0];
                if (['txt', 'nsh', 'sql', 'sh'].includes(ext.toLowerCase())) force = true;
            } catch { }
            if (_data.mode === "portal") {
                const mod_id = _data["ng.build"].id.split(".")[1];
                editor = await this.portalWorkspace.FileEditor(mod_id, _data);
            }
            else editor = this.workspace.FileEditor(_data, {}, force);
        }
        else if (_type === "route") {
            if (_data.mode === "portal") {
                const mod_id = _data["ng.build"].id.split(".")[1];
                editor = await this.portalWorkspace.RouteEditor(mod_id, _data);
            }
            else editor = this.workspace.RouteEditor(_data);
        }
        if (!editor) return;
        await editor.open(0);
        await this.service.render(100);
        await editor.activate();
    }
}