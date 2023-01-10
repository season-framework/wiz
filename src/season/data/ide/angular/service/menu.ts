import Service from './service';

export default class Menu {

    public mode: any;
    public top: any = [];
    public bottom: any = [];
    public width: any = null;

    constructor(private service: Service, mode: any = null) {
        this.mode = mode;
    }

    public async toggle(item: any) {
        if (!item) {
            this.mode = null;
        } else if (this.mode == item.id) {
            this.mode = null;
        } else {
            this.mode = item.id;
            if (item.width) this.width = item.width;
            else this.width = 360;
        }
        await this.service.render();
    }

    public async build(top: any = [], bottom: any = []) {
        if (!top) top = [];
        if (!bottom) bottom = [];
        this.top = [];
        this.bottom = [];

        for (let i = 0; i < top.length; i++)
            this.top.push(top[i]);

        if (bottom)
            for (let i = 0; i < bottom.length; i++)
                this.bottom.push(bottom[i]);

        await this.service.render();
    }

    public isActive(mode) {
        return this.mode == mode ? 'active' : '';
    }
}
