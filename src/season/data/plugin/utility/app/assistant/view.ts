import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import showdown from 'showdown';

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public message: string = "";
    public data: any = null;
    public loading: any = false;

    constructor(public service: Service) { }

    public async reset() {
        this.loading = true;
        await this.service.render();
        await wiz.call("reset");
        this.loading = false;
        await this.service.render();
    }

    public async send(message: string) {
        this.data = null;
        this.loading = true;
        await this.service.render();

        let { data } = await wiz.call("request", { query: message });
        this.data = data;
        this.loading = false;
        await this.service.render();
    }

    public showdown(text) {
        let converter = new showdown.Converter();
        return converter.makeHtml(text);
    }

}