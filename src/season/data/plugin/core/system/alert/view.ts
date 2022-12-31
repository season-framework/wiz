import { OnInit, Input } from '@angular/core';

export class Component implements OnInit {
    @Input() model: any;

    public async ngOnInit() {
    }
}