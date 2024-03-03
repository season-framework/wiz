import { OnInit, Input } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    @Input() config: any = {};

    public title: any = { text: '', icon: '' };
    public status: string = '';
    public statusOpened: boolean = false;

    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.service.init();
        await this.service.render();
        this.config.setTitle = this.setTitle.bind(this);
        this.config.setStatus = this.setStatus.bind(this);
        this.config.alert = this.alert;
        if (this.config.onLoad) await this.config.onLoad();
    }

    public async setTitle(text: string, icon: string = '') {
        this.title.text = text;
        this.title.icon = icon;
        await this.service.render();
    }

    public async setStatus(status: string) {
        this.status = status;
        await this.service.render();
    }

    public statusColor() {
        if (this.status == 'error') return 'bg-red-lt';
        if (this.status == 'warning') return 'bg-yellow-lt';
        if (this.status == 'info') return 'bg-blue-lt';
        return '';
    }

    public async alertToggle() {
        this.statusOpened = !this.statusOpened;
        await this.service.render();
    }

    public alert: any = {
        data: [],
        load: () => {
            let tmp = [];
            for (let i = 0; i < this.alert.data.length; i++) {
                tmp.push(this.alert.data[i]);
                if (tmp.length >= 5) break;
            }
            return tmp;
        },
        display: () => {
            let alerts = this.alert.data;
            let status = 0;
            let statusmap = { 'error': 3, 'warning': 2, 'info': 1, 'message': 0 };
            let statusrmap = { 0: 'message', 1: 'info', 2: 'warning', 3: 'error' };
            for (let i = 0; i < alerts.length; i++) {
                let statuscode = statusmap[alerts[i].status];
                if (statuscode > status)
                    status = statuscode;
            }

            this.status = statusrmap[status];

            if (alerts.length == 0) {
                this.statusOpened = false;
                return "";
            } else if (alerts.length == 1) {
                return alerts[0].message;
            }
            return `${alerts.length} messages`;
        },
        create: async (status: string, message: string, autoHide: number = 0) => {
            let _alert = {};
            _alert.message = message;
            _alert.status = status;
            _alert.alive = true;

            _alert.update = async (msg: string) => {
                _alert.message = msg;
                await this.service.render();
            }

            _alert.hide = async (timeout: number = 0) => {
                if (timeout > 0) await this.service.render(timeout);
                this.alert.data.remove(_alert);
                this.alert.display();
                await this.service.render();
                _alert.alive = false;
            }

            this.alert.data.push(_alert);
            if (autoHide > 0)
                _alert.hide(autoHide);

            this.alert.display();
            await this.service.render();

            return _alert;
        },
        error: async (message: string, autoHide: number = 0) => await this.alert.create('error', message, autoHide),
        warning: async (message: string, autoHide: number = 0) => await this.alert.create('warning', message, autoHide),
        info: async (message: string, autoHide: number = 0) => await this.alert.create('info', message, autoHide),
        message: async (message: string, autoHide: number = 0) => await this.alert.create('message', message, autoHide)
    };

}