import { OnInit } from "@angular/core";
import toastr from 'toastr';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.service.init();
        const { code, data } = await wiz.call("data", {});
        toastr.success(`Hello, World!`);
    }

}