import Service from './service';

export default class Statusbar {
    public data: any = null;

    constructor(private service: Service) { }

    public generate(message: any) {
        let obj: any = {};
        obj.status_id = new Date().getTime();
        obj.message = message;
        obj.hide = async (timeout: number = 0) => {
            await this.service.render(timeout);
            if (!this.data) return;
            if (this.data.status_id != obj.status_id)
                return;
            await this.hide();
        }
        return obj;
    }

    public async show(message: any, timeout: number = 0) {
        this.data = this.generate(message);
        await this.service.render();
        if (timeout > 0)
            await this.data.hide(timeout);
    }

    public async info(message: any, timeout: number = 0) {
        this.data = this.generate(message);
        this.data.mode = 'info';
        await this.service.render();
        if (timeout > 0)
            await this.data.hide(timeout);
    }

    public async error(message: any, timeout: number = 0) {
        this.data = this.generate(message);
        this.data.mode = 'error';
        await this.service.render();
        if (timeout > 0)
            await this.data.hide(timeout);
    }

    public async warning(message: any, timeout: number = 0) {
        this.data = this.generate(message);
        this.data.mode = 'warning';
        await this.service.render();
        if (timeout > 0)
            await this.data.hide(timeout);
    }

    public async process(message: any, timeout: number = 0) {
        this.data = this.generate(message);
        this.data.mode = 'process';
        await this.service.render();
        if (timeout > 0)
            await this.data.hide(timeout);
    }

    public async hide(timeout: number = 0) {
        await this.service.render(timeout);
        this.data = null;
        await this.service.render();
    }
}