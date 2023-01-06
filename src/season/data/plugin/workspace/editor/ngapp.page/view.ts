import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() editor;

    public data: any = {};
    public loading: boolean = true;
    public layout: any = [];
    public ctrls: any = [];

    constructor(public service: Service) { }

    public async ngOnInit() {
        let res = await wiz.app("workspace.app.explore").call("layout");
        this.layout = res.data;
        this.data = await this.editor.tab().data();
        this.loading = false;
        this.ctrls = await this.loadControllers();
        await this.service.render();
    }

    public async loadControllers() {
        let { data } = await wiz.app("workspace.app.explore").call("controller");
        return data;
    }

    public async download() {
        let target = wiz.url("download/" + this.data.id);
        window.open(target, '_blank');
    }
}