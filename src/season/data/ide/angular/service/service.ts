import { Injectable } from '@angular/core';
import File from './file';
import Alert from './alert';
import Statusbar from './statusbar';
import Loading from './loading';
import Editor from './editor';
import Menu from './menu';
import Event from './event';
import Shortcut from './shortcut';

@Injectable({ providedIn: 'root' })
export class Service {
    public file: File;
    public alert: Alert;
    public statusbar: Statusbar;
    public loading: Loading;
    public editor: Editor;
    public event: Event;

    public leftmenu: Menu;
    public rightmenu: Menu;
    public overlay: Menu;

    public shortcut: Shortcut;
    public app: any;

    constructor() { }

    public async init(app: any) {
        if (app) {
            this.app = app;
            this.file = new File(this);
            this.alert = new Alert(this);
            this.statusbar = new Statusbar(this);
            this.loading = new Loading(this);
            this.editor = new Editor(this);
            this.event = new Event(this);
            this.leftmenu = new Menu(this, 'workspace.app.list');
            this.rightmenu = new Menu(this, null);
            this.overlay = new Menu(this, null);
            this.shortcut = new Shortcut(this);

            await this.shortcut.bindDefault();
        }
        return this;
    }

    public async log(value: any, tag: string = "ide") {
        const Style = {
            base: [
                "color: #fff",
                "background-color: #444",
                "padding: 2px 4px",
                "border-radius: 2px"
            ],
            ide: [
                "background-color: blue"
            ],
            server: [
                "background-color: green"
            ]
        }

        if (tag == 'server') {
            let style = Style.base.join(';') + ';';
            style += Style.server.join(';');
            console.log(`%cwiz.was%c ` + value, style, null);
            if (value.includes(`[build][error]`)) {
                await this.statusbar.error("error on build");
            } else if (value.includes(`EsBuild complete in`)) {
                await this.statusbar.info("build finish", 5000);
            }
        } else {
            let style = Style.base.join(';') + ';';
            style += Style.ide.join(';');
            console.log(`%cwiz.ide%c`, style, null, value);
        }
    }

    public async render(time: number = 0) {
        let timeout = () => new Promise((resolve) => {
            setTimeout(resolve, time);
        });
        if (time > 0) {
            this.app.ref.detectChanges();
            await timeout();
        }
        this.app.ref.detectChanges();
    }

    public href(url: any) {
        this.app.router.navigate(url);
    }

    public random(stringLength: number = 16) {
        const fchars = 'abcdefghiklmnopqrstuvwxyz';
        const chars = '0123456789abcdefghiklmnopqrstuvwxyz';
        let randomstring = '';
        for (let i = 0; i < stringLength; i++) {
            let rnum: any = null;
            if (i === 0) {
                rnum = Math.floor(Math.random() * fchars.length);
                randomstring += fchars.substring(rnum, rnum + 1);
            } else {
                rnum = Math.floor(Math.random() * chars.length);
                randomstring += chars.substring(rnum, rnum + 1);
            }
        }
        return randomstring;
    }

}

export default Service;
