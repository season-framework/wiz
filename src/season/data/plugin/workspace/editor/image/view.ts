import { OnInit, Input, ChangeDetectorRef } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() editor;
    private id = '';
    public src: any = null;
    public width = 0;
    public height = 0;
    private bgcolor: "white" | "gray" | "black" = "gray";
    public loading: boolean = true;

    constructor(
        public service: Service,
        public ref: ChangeDetectorRef,
    ) { }

    public async ngOnInit() {
        this.id = Math.random().toString(36).slice(2);
        const { data } = await this.editor.tab().data();
        if (!data) return;
        this.src = wiz.url(`read/${data}`);
        this.loading = false;
        await this.service.render();
    }

    public async load(e: any) {
        const { naturalWidth, naturalHeight } = e.target;
        this.width = naturalWidth;
        this.height = naturalHeight;
        await this.service.render();
    }

    public async change(bg: any) {
        this.bgcolor = bg;
        await this.service.render();
    }
}