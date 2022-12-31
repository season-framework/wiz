import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class Util {
    public value: string = '';

    get data() {
        return this.value;
    }

    set data(value: string) {
        this.value = value;
    }

}

export default Util;