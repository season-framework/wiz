import Service from './service';

export default class Alert {

    public isshow: boolean = false;
    public callback: any = null;
    public hide: any = async () => { };
    public action: any = async () => { };
    public default_opts: any = {
        title: 'Are you sure?',
        message: "Do you really want to remove app? What you've done cannot be undone.",
        action: "Delete",
        actionBtn: "error",
        cancel: true,
        status: 'error'
    };
    public opts: any = {};

    constructor(private service: Service) { }

    public async show(mopts: any = {}) {
        this.isshow = true;
        this.opts = JSON.parse(JSON.stringify(this.default_opts));
        for (let key in mopts)
            this.opts[key] = mopts[key];
        await this.service.render();

        let fn = () => new Promise((resolve) => {
            this.hide = async () => {
                this.isshow = false;
                await this.service.render();
                resolve(false);
            }

            this.action = async () => {
                this.isshow = false;
                await this.service.render();
                resolve(true);
            }
        });

        return await fn();
    }

    public localize(mopts: any = {}) {
        let alert = new Alert(this.service);
        for (let key in mopts)
            alert.default_opts[key] = mopts[key];
        return alert;
    }

    public async error(message) {
        await this.show({ title: '[Error]', message: message, action: "Close", actionBtn: "error", cancel: false });
    }

    public async warning(message) {
        await this.show({ title: '[Warning]', message: message, action: "Close", actionBtn: "warning", cancel: false });
    }

    public async info(message) {
        await this.show({ title: '[Info]', message: message, action: "Close", actionBtn: "success", cancel: false });
    }

    public async success(message) {
        await this.show({ title: '[Success]', message: message, action: "Close", actionBtn: "success", cancel: false });
    }
}