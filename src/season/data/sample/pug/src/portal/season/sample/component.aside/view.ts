import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }
    public async ngOnInit() {
        await this.service.init();
    }

    public isMenuCollapsed: boolean = true;

    public menuActive(url: string) {
        let path = location.pathname;
        if (path.indexOf(url) == 0) return 'active';
        return '';
    }
}