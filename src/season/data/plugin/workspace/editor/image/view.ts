import { OnInit, Input, ChangeDetectorRef } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    @Input() editor;
    private id = '';
    public src: string = "";
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
        this.src = `${wiz.url("read")}?path=${encodeURIComponent(data)}`;
        this.loading = false;
        await this.service.render();
    }

    private load(e) {
        const { naturalWidth, naturalHeight } = e.target;
        this.width = naturalWidth;
        this.height = naturalHeight;
    }

    private change(bg) {
        this.bgcolor = bg;
        this.ref.detectChanges();
    }
}