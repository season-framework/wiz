import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import MonacoEditor from "@wiz/app/core.editor.monaco";

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public item: any = null;

    constructor(public service: Service) { }

    public async ngOnInit() {
    }

    private async update(path: string, data: string) {
        let res = await wiz.call('update', { path: path, code: data });
        await this.service.statusbar.warning("build project...");
        res = await wiz.call('build');
        if (res.code == 200) await this.service.statusbar.info("build finish", 5000);
        else await this.service.statusbar.error("error on build");
    }

    public async open(name) {
        let configpath = name + ".py";
        let language = "python";
        if (name == "plugin") {
            configpath = name + ".json";
            language = "json";
        }
        if (name == "shortcut") {
            configpath = name + ".ts";
            language = "typescript";
        }

        let editor = this.service.editor.create({
            component_id: this.APP_ID,
            path: "/config/" + configpath,
            title: name,
            unique: true,
            current: 0
        });

        editor.create({
            name: 'config',
            viewref: MonacoEditor,
            path: "/config/" + configpath,
            config: { monaco: { language: language } }
        }).bind('data', async (tab) => {
            let { code, data } = await wiz.call('load', { path: configpath });
            if (code != 200) return {};
            return { data };
        }).bind('update', async (tab) => {
            let data = await tab.data();
            await this.update(configpath, data.data);
        });

        await editor.open();
    }

}