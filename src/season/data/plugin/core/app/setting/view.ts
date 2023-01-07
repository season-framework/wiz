import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import toastr from "toastr";
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

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public item: any = null;

    constructor(public service: Service) { }

    public async ngOnInit() {
    }

    private async update(path: string, data: string) {
        let res = await wiz.call('update', { path: path, code: data });
        if (res.code == 200) toastr.success("Updated");
        res = await wiz.call('build');
        if (res.code == 200) toastr.info("Build Finish");
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