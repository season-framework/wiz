import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public data: any = [];
    public keyword: string = "";
    public loading: boolean = false;

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.load();
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public match(value: string) {
        if (value.toLowerCase().indexOf(this.keyword.toLowerCase()) >= 0)
            return true;
        return false;
    }

    public async install(keyword: string) {
        if (!keyword) return;
        await this.loader(true);
        let { data } = await wiz.call("install", { package: keyword });
        this.service.log(data);
        await this.load();
        await this.loader(false);
    }

    public async load() {
        await this.loader(true);
        let { data } = await wiz.call("list");
        data.sort((a, b) => {
            return a.name.localeCompare(b.name);
        });
        this.data = data;
        await this.loader(false);
    }
}