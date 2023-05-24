import { OnInit, Output, EventEmitter } from '@angular/core';
import { Service } from '@wiz/service/service';
import { DomSanitizer } from '@angular/platform-browser';

export class Component implements OnInit {
    @Output() binding = new EventEmitter<any>();

    public APP_ID: string = wiz.namespace;
    public loading: boolean = false;
    public url: string = "/";
    public urlSafe: string;

    constructor(private sanitizer: DomSanitizer, public service: Service) {
        this.urlSafe = sanitizer.bypassSecurityTrustResourceUrl("/");
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public async ngOnInit() {
        let id = this.APP_ID;
        let data = this;
        this.binding.emit({ id, data });
    }

    public async move(url: any) {
        if (!url) url = this.url;
        if (!url) url = "/";
        if (url[0] != "/") url = "/" + url;
        this.url = url;
        this.urlSafe = this.sanitizer.bypassSecurityTrustResourceUrl(url);
        await this.service.render();
    }

}