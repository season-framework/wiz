import { OnInit, OnDestroy, ElementRef, ViewChild } from '@angular/core';
import { Service } from '@wiz/service/service';
import { io } from "socket.io-client";
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { SearchAddon } from '@xterm/addon-search';
import { WebLinksAddon } from '@xterm/addon-web-links';

export class Component implements OnInit, OnDestroy {
    @ViewChild('terminal')
    public terminal: ElementRef;

    public socket: any;
    public term: any;
    public fit: any;
    public namespace: any;

    public APP_ID: string = wiz.namespace;

    constructor(public service: Service) { }

    public async socketEmit(channel: string, data: any = {}) {
        data.namespace = this.namespace;
        this.socket.emit(channel, data);
    }

    public async ngOnInit() {
        await this.service.render();

        const generateRandomString = (num) => {
            const characters = 'abcdefghijklmnopqrstuvwxyz';
            let result = '';
            const charactersLength = characters.length;
            for (let i = 0; i < num; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }

        this.namespace = generateRandomString(8);

        const modw = 9;
        const modh = 17;

        let { offsetWidth, offsetHeight } = this.terminal.nativeElement;

        let cols = Math.floor(offsetWidth / modw) - 1;
        let rows = Math.floor(offsetHeight / modh);

        await this.service.render();
        const term = new Terminal({ cursorBlink: true, macOptionIsMeta: true });
        const fit = new FitAddon();
        term.loadAddon(new WebLinksAddon());
        term.loadAddon(new SearchAddon());
        term.loadAddon(fit);

        term.resize(cols, rows);

        term.open(this.terminal.nativeElement);
        term.writeln("Welcome to wiz terminal!");
        term.writeln('');

        const socket = io.connect("/wiz/ide/app/xterm.app.term");;

        term.onData((data) => {
            this.socketEmit("ptyinput", { input: data })
        });

        socket.on("ptyoutput", async (data) => {
            term.write(data.output);
        });

        socket.on("connect", () => {
            fitToscreen();
            const dims = { cols: term.cols, rows: term.rows };
            this.socketEmit("join");
            this.socketEmit("create", dims);
        });

        socket.on("disconnect", () => {
        });

        let fitToscreen = () => {
            fit.fit();
            const dims = { cols: term.cols, rows: term.rows };
            this.socketEmit("resize", dims);
        }

        this.socket = socket;
    }

    public async ngOnDestroy() {
        this.socketEmit('close');
        this.socket.close();
    }
}