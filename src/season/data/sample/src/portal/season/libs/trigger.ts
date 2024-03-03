export default class Trigger {
    public value: any = {};

    constructor() { }

    public bind(name: string, fn: any) {
        this.value[name] = fn;
    }

    public unbind(name: string) {
        delete this.value[name];
    }

    public async call(name: string) {
        if (this.value[name])
            await this.value[name]();
    }

}