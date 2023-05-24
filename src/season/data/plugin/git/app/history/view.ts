import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';
import moment from "moment";

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public loading: boolean = true;

    public commits: any = [];

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.load();
    }

    public datedisplay(date) {
        let targetdate = moment(date);
        let diff = new Date().getTime() - new Date(targetdate).getTime();
        diff = diff / 1000 / 60 / 60;

        if (diff > 24) return targetdate.format("YYYY-MM-DD hh:mm");
        if (diff > 1) return Math.floor(diff) + " hours ago"

        diff = diff * 60;

        if (diff < 2) return "just now";

        return Math.floor(diff) + " minutes ago";
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public async load() {
        await this.loader(true);
        let { data } = await wiz.call("history");
        this.commits = data;
        await this.loader(false);
    }
}