import { OnInit, AfterViewInit, ChangeDetectorRef, ViewChild } from '@angular/core';
import { Service } from "@wiz/service/service";
import { Workspace } from 'src/app/workspace.app.explore/service';

let timeoutId = null;

export class Component implements OnInit, AfterViewInit {
    private list = [];
    private text = "";
    private idx = -1;
    private root = "src";

    @ViewChild("searchInput") searchInput;

    constructor(
        public ref: ChangeDetectorRef,
        public service: Service
    ) {
        this.workspace = new Workspace(service, wiz);
    }

    public ngOnInit() {
        this.list = [];
        this.text = "";
        this.idx = -1;
        this.render();
    }

    public ngAfterViewInit() {
        try {
            this.searchInput.nativeElement.focus();
        } catch { }
    }

    private render() {
        this.ref.detectChanges();
    }

    private clear() {
        this.list = [];
        this.render();
    }

    private async open() {
        if (this.idx < 0) return;
        if (this.list.length === 0) return;

        const path = `${this.root}/${this.list[this.idx]}`;
        const { code, data } = await wiz.call("load", { path });
        if (code !== 200) return;
        const _type = data.type;
        const _data = data.data;
        let editor = null;
        if (_type === "app") {
            editor = this.workspace.AppEditor(_data);
        }
        else if (_type === "file") {
            editor = this.workspace.FileEditor(_data);
        }
        else if (_type === "route") {
            editor = this.workspace.RouteEditor(_data);
        }
        if (!editor) return;
        await editor.open(0);
        await this.service.render(100);
        await editor.activate();
        await this.service.overlay.toggle();
    }

    private onKeydown(e) {
        const { key } = e;
        if (this.list.length === 0) return;
        if (key === "ArrowUp") {
            e.preventDefault();
            this.idx--;
            if (this.idx < 0) this.idx = this.list.length - 1;
        }
        else if (key === "ArrowDown") {
            e.preventDefault();
            this.idx++;
            if (this.idx >= this.list.length) this.idx = 0;
        }
        else if (key === "Enter") {
            e.preventDefault();
            this.open();
            return;
        }
        this.render();
    }

    private rootMap(root) {
        const src = ['s', 'src'];
        // const portal = ['p', 'portal'];
        const config = ['c', 'config', 'conf'];

        if (src.includes(root)) return "src";
        // if (portal.includes(root)) return "portal";
        if (config.includes(root)) return "config";
    }

    private onChange() {
        this.idx = -1;
        const text = this.text;
        if (text.length === 0) {
            this.clear();
            return;
        }

        const arr = text.split(" ");
        const root = this.rootMap(arr[0]);
        if (root && arr.length >= 2 && root !== this.root) {
            this.root = root;
            this.text = arr.slice(1).join(" ");
            this.render();
        }

        if (text.length === 0) return;
        try {
            clearTimeout(timeoutId);
        } catch { }
        timeoutId = setTimeout(async () => {
            const { code, data } = await wiz.call("search", { root: this.root, text });
            if (code !== 200) {
                this.clear();
                return;
            }

            this.list = data;
            if (this.list.length > 0) this.idx = 0;
            this.render();
        }, 500);

    }
}