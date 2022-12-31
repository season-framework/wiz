import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() editor;

    public data: any = {};
    public ctrls: any = [];
    public loading: boolean = true;

    constructor(public service: Service) { }

    public async ngOnInit() {
        this.data = await this.editor.tab().data();
        this.loading = false;
        if (this.editor.ctrls) this.ctrls = this.editor.ctrls;
        else this.ctrls = await this.loadControllers();
        await this.service.render();
    }

    public async loadControllers() {
        let { data } = await wiz.app("workspace.app.list").call("controllers");
        return data;
    }
}