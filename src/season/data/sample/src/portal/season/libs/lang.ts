import Service from './service';

export default class Lang {
    public value: any;

    constructor(public service: Service) { }

    public async set(lang: string) {
        this.value = lang;
        this.service.app.translate.use(lang);
        await this.service.render();
    }

    public get() {
        return this.value;
    }

    public is(lang: string) {
        return this.value == lang;
    }

    public async translate(key: string) {
        let fn: any = () => new Promise((resolve) => {
            this.service.app.translate.get(key, { value: '' }).subscribe((res: string) => {
                resolve(res);
            });
        })
        return await fn();
    }
}