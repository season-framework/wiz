import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() menu;

    constructor(public service: Service) { }

    public async ngOnInit() {
    }
}