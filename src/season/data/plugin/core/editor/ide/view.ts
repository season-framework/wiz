import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() editor: any;

    public data: any = {};
    public loading: boolean = true;

    constructor(public service: Service) { }

    public async ngOnInit() {
        this.data = await this.editor.tab().data();
        this.loading = false;
        await this.service.render();
    }

    public async download() {
        let namespace = this.data.mod_id + "." + this.data.mod_type + "." + this.data.id;
        let target = wiz.url("download/" + namespace);
        window.open(target, '_blank');
    }
}