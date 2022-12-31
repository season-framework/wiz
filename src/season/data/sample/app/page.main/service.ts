import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class Users {
    public name: string = 'John';
    public surname: string = 'Doe';

    get username() {
        return `${this.name} ${this.surname}`;
    }

    set username(value: string) {
        [this.name, this.surname] = value.split(" ");
    }
}

export default Users;