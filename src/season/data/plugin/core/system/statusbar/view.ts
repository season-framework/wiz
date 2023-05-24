import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    public status: any = {};

    constructor(public service: Service) { }

    public async ngOnInit() {
        const { data } = await wiz.call("status");
        this.status = data;
    }
}