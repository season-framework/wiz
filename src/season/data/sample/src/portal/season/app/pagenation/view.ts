import { OnInit, Input, Output, EventEmitter, OnChanges } from '@angular/core';

export class Component implements OnInit, OnChanges {
    @Input() current: any = 1;
    @Input() start: any = 1;
    @Input() end: any = 1;
    @Input() maxlength: any = 10;
    @Output() pageMove = new EventEmitter<number>();

    public list: Array<number> = [];

    public async ngOnInit() {
        this.Math = Math;
    }

    public async ngOnChanges() {
        this.list = [];
        for (let i = 0; i < this.maxlength; i++) {
            if (this.start + i > this.end) break;
            this.list.push(this.start + i);
        }
    }

    public move(page: number) {
        this.pageMove.emit(page);
    }
}