import { OnInit } from '@angular/core';
import { Service } from '@wiz/libs/portal/season/service';

export class Component implements OnInit {
    constructor(public service: Service) { }

    public async ngOnInit() {
        await this.service.init();
        await this.service.auth.allow(false, "/");
    }

    public data: any = {
        username: '',
        password: ''
    };

    public async alert(message: string, status: string = 'error') {
        return await this.service.alert.show({
            title: "",
            message: message,
            cancel: false,
            actionBtn: status,
            action: "확인",
            status: status
        });
    }

    public async login() {
        let user = JSON.parse(JSON.stringify(this.data));
        user.password = this.service.auth.hash(user.password);

        let { code, data } = await wiz.call("login", user);
        if (code == 200) {
            location.href = "/";
            return;
        }
        await this.alert(data);
    }
}