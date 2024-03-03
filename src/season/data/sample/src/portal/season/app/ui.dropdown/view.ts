import { OnInit } from '@angular/core';
import { Input } from '@angular/core';
import { ContentChild, TemplateRef } from '@angular/core';
import { HostListener } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    @Input() menuStyle: any = {};

    constructor(public service: Service) { }

    public isOpen: boolean = false;

    @ContentChild('button') button: TemplateRef<any>;
    @ContentChild('menu') menu: TemplateRef<any>;

    public async ngOnInit() { }

    public async toggle(stat: any = null) {
        if (stat !== null) {
            this.isOpen = stat;
        } else {
            this.isOpen = !this.isOpen;
        }
        await this.service.render();
    }

    @HostListener('document:click')
    public clickout() {
        if (this.isOpen)
            this.isOpen = false;
        this.service.render();
    }
}