import Service from './service';

export default class Event {

    public data: any = {};

    constructor(private service: Service) { }

    public bind(namespace: string, value: any) {
        this.data[namespace] = value;
    }

    public load(namespace: string) {
        return this.data[namespace];
    }
}
