import { OnInit, AfterViewInit, ChangeDetectorRef, ViewChild } from '@angular/core';
import { Service } from "@wiz/service/service";
import { Workspace } from 'src/app/workspace.app.explore/service';

let timeoutId = null;

export class Component implements OnInit, AfterViewInit {
    private list = [];
    private display = [];
    private text = "";
    private idx = -1;
    private root = "src";
    private showRoot = false;

    @ViewChild("searchInput") searchInput;

    constructor(
        public ref: ChangeDetectorRef,
        public service: Service
    ) {
        this.workspace = new Workspace(service, wiz);
    }

    public ngOnInit() {
        this.list = [];
        this.display = [];
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
        this.display = [];
        this.render();
    }

    private async open(i = null) {
        if (i !== null) this.idx = i;
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
        const portal = ['p', 'portal'];
        const config = ['c', 'config', 'conf'];

        if (src.includes(root)) return "src";
        if (portal.includes(root)) return "portal";
        if (config.includes(root)) return "config";
        if (root === "#root") {
            this.showRoot = !this.showRoot;
            this.clear();
            this.text = "";
            this.idx = -1;
            this.render();
        }
    }

    private highlight(list, text) {
        const targets = text.split(" ");
        const _s1 = `<strong class="text-bg-youtube">`;
        const _s2 = `</strong>`;
        const ou = _s1.length + _s2.length; // offset unit
        return list.map(item => {
            const arr = [];
            targets.forEach(t => {
                if (t.replace(/\s/g, "").length === 0) return;
                [...item.matchAll(new RegExp(t, "gi"))].forEach(it => {
                    arr.push({
                        index: it.index,
                        length: t.length,
                    });
                });
            });
            let offset = 0;
            let res = item;
            for (let i = 0; i < arr.length; i++) {
                const { index, length } = arr[i];
                const s = index + offset;
                const e = s + length;
                const before = res.slice(0, s);
                const text = res.slice(s, e);
                const after = res.slice(e);
                res = `${before}${_s1}${text}${_s2}${after}`;
                offset += ou;
            }
            return res;
        });
    }

    private onChange() {
        this.idx = -1;
        try {
            this.text = this.text.toLowerCase();
            this.render();
        }catch {}
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
            this.clear();
        }

        if (text.length === 0) return;
        try {
            clearTimeout(timeoutId);
        } catch { }
        timeoutId = setTimeout(async () => {
            if (this.text.length === 0) return;
            const { code, data } = await wiz.call("search", { root: this.root, text });
            if (code !== 200) {
                this.clear();
                return;
            }
            this.list = data;
            this.display = this.highlight(data, text);
            if (this.list.length > 0) this.idx = 0;
            this.render();
        }, 500);

    }
}