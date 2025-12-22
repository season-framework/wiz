import { Input } from '@angular/core';

export class Component {
    @Input() title = "Wiznav";

    public isMenuCollapsed: boolean = true;

    constructor() { }

    view = (() => {
        let obj: any = {};

        obj.data = "";

        obj.click = async () => {
            alert(obj.data);
        }

        return obj;
    })();

}