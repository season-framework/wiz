import { OnInit } from "@angular/core";
import toastr from 'toastr';

// import global service
import Util from '@wiz/service/util';

// import local service
import Users from "./service";

// use directives and dependencies
@directives({
    HighlightDirective: '@wiz/libs/directives/highlight.directive'
})
@dependencies({
    MatIconModule: '@angular/material/icon',
    MatInputModule: '@angular/material/input',
    BrowserAnimationsModule: '@angular/platform-browser/animations'
})
export class Component implements OnInit {

    constructor(public util: Util, public user: Users) {
        util.data = 'test';
        console.log(util);
    }

    public async ngOnInit() {
        toastr.success(`Hello, ${this.user.username}!`);
    }

}