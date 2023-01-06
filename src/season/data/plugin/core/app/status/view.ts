import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public data: any = {};
    public interval_id: any = 0;

    constructor(public service: Service) { }

    public timer(time) {
        let minute = Math.round(time / 60);
        if (minute == 0) return time + " sec";
        let hour = Math.round(minute / 60);
        if (hour == 0) return minute + " min";
        return hour + " hr"
    }

    public async ngOnInit() {
        let { data } = await wiz.call("status");
        this.data = data;
        await this.service.render();

        this.interval_id = setInterval(async () => {
            let { data } = await wiz.call("status");
            this.data = data;
            await this.service.render();
        }, 1000);

    }

    public async ngOnDestroy() {
        if (this.interval_id > 0)
            clearInterval(this.interval_id);
    }

    public async restart() {
        await this.service.loading.show();
        try {
            await wiz.call("restart");
        } catch (e) {
        }

        while (true) {
            try {
                await wiz.call("status");
                break;
            } catch (e) {
                await this.service.render(500);
            }
        }
        await this.service.loading.hide();
    }

}