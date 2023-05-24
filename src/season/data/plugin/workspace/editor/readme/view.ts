import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';
import showdown from 'showdown';

export class Component implements OnInit {
    @Input() editor;

    public loading: boolean = true;
    public data: any = {};

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.loader(true);
        this.data = await this.editor.tab().data();
        await this.loader(false);
    }

    public showdown(text) {
        let converter = new showdown.Converter();
        return converter.makeHtml(text);
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

}