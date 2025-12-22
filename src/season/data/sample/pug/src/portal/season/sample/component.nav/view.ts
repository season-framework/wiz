import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    public isMenuCollapsed: boolean = true;

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.service.init();
    }
}