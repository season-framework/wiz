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
    public items: any = [];

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.load();
    }

    public active(item: any) {
        let em = this.service.editor;
        if (!em.activated) return '';
        if (this.APP_ID != em.activated.component_id) return '';
        if (item.path != em.activated.path) return '';
        return 'active';
    }

    public async load() {
        this.items = [
            {
                title: 'Web Config', subtitle: 'ng.component', path: 'angular/ui',
                files: [
                    { name: 'index', path: 'angular/index.pug', lang: 'pug' },
                    { name: 'web resources', path: 'angular/angular.build.options.json', lang: 'json' }
                ]
            },
            {
                title: 'Advanced', subtitle: 'ng.advanced', path: 'angular/advanced',
                files: [
                    { name: 'module', path: 'angular/app/app.module.ts', lang: 'typescript' },
                    { name: 'routing', path: 'angular/app/app-routing.module.ts', lang: 'typescript' },
                    { name: 'wiz', path: 'angular/wiz.ts', lang: 'typescript' },
                    { name: 'app', path: 'angular/app/app.component.pug', lang: 'pug' },
                    { name: 'component', path: 'angular/app/app.component.ts', lang: 'typescript' },
                    { name: 'scss', path: 'angular/app/app.component.scss', lang: 'scss' }
                ]
            }
        ];

        await this.service.render();
    }

    private async update(path: string, data: string) {
        let res = await wiz.call('update', { path: path, code: data });
        if (res.code != 200) return;
        toastr.success("Updated");
        res = await wiz.call('build', { path: path });
        if (res.code == 200) toastr.info("Build Finish");
        else toastr.error("Error on build");
    }

    public async open(item: any) {
        let editor = this.service.editor.create({
            component_id: this.APP_ID,
            path: item.path,
            title: item.title,
            subtitle: item.subtitle,
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
                let { code, data } = await wiz.call('data', { path: tab.path });
                if (code != 200) return {};
                return { data };
            }).bind('update', async (tab) => {
                let data = await tab.data();
                await this.update(tab.path, data.data);
            });
        }

        if (!item.files) {
            createTab(item.path, item.lang);
        } else {
            for (let i = 0; i < item.files.length; i++) {
                createTab(item.files[i].path, item.files[i].lang, item.files[i].name);
            }
        }

        await editor.open();
    }
}