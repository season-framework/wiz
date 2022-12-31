import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;

    public data: string = '';
    public pug: any = "";

    public monaco: any = {
        language: 'html',
        wordWrap: false,
        roundedSelection: false,
        scrollBeyondLastLine: true,
        glyphMargin: false,
        folding: true,
        fontSize: 14,
        automaticLayout: true,
        minimap: { enabled: false }
    }

    public monacoPug: any = {
        language: 'pug',
        lineNumbers: 'off',
        wordWrap: false,
        roundedSelection: false,
        scrollBeyondLastLine: true,
        glyphMargin: false,
        folding: true,
        fontSize: 14,
        automaticLayout: true,
        readOnly: true,
        minimap: { enabled: false }
    }

    constructor(public service: Service) { }

    public async convert() {
        let { data } = await wiz.call("html2pug", { html: this.data });
        this.pug = data;
        await this.service.render();
    }

}