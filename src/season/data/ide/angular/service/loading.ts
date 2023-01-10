import Service from './service';

export default class Loading {

    public isshow: boolean = false;
    public opts: any = {};

    constructor(private service: Service) { }

    public async show(mopts: any = {}) {
        this.isshow = true;
        this.opts = {};
        for (let key in mopts)
            this.opts[key] = mopts[key];
        await this.service.render();
    }

    public async hide() {
        this.isshow = false;
        await this.service.render();
    }

}