import { OnInit, Input } from '@angular/core';

export class Component implements OnInit {
    @Input() height: number = 36;

    constructor() { }

    public async ngOnInit() {
    }
}