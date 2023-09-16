import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    constructor(private service: Service) { }

    @Input() height: number = 48;
    public WIZ_IDE_URI: string = WIZ_IDE_URI;

    public async ngOnInit() {
    }
}