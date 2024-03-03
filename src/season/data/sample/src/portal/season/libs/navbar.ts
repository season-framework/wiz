import Service from './service';

export default class Navbar {

    public isMenuCollapsed: boolean = true;
    public subnav: string = "default";

    constructor(public service: Service) { }

    public async set(subnav: string) {
        this.subnav = subnav;
        await this.service.render();
    }

    public is(target: string) {
        return this.subnav == target;
    }

    public async toggle(collapsed: any = null) {
        if (collapsed == null)
            this.isMenuCollapsed = !this.isMenuCollapsed;
        else if (collapsed)
            this.isMenuCollapsed = true;
        else
            this.isMenuCollapsed = false;
        await this.service.render();
    }

}