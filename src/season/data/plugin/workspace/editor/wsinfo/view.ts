import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() editor;

    public data: any = { id: null, git: { author: {}, remote: [] } };
    public loading: boolean = true;

    constructor(public service: Service) { }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public async ngOnInit() {
        let data = await this.editor.tab().data();
        this.data = data;
        await this.git();
        await this.loader(false);
    }

    public async download() {
        let target = wiz.url("download/" + this.data.project);
        window.open(target, '_blank');
    }

    public async git() {
        let path = this.data.project;
        let { code, data } = await wiz.call("git", { path })
        this.data.git = data;
    }

    public async update_git(name: string, email: string) {
        await this.loader(true);
        let path = this.data.project;
        await wiz.call("git_update", { path, name, email });
        await this.git();
        await this.loader(false);
    }

    public async rebuild() {
        await this.service.loading.show();
        let path = this.data.project;
        await wiz.call("rebuild", { path });
        await this.service.loading.hide();
    }

    public async delete() {
        let res = await this.service.alert.show({ title: 'Delete', message: `Are you sure to delete '${this.data.project}' project?`, action_text: "Delete", action_class: "btn-danger" });
        if (!res) return;

        await this.service.loading.show();
        let path = this.data.project;
        await wiz.call("delete", { path });
        await this.service.loading.hide();
        this.editor.close();
    }
}