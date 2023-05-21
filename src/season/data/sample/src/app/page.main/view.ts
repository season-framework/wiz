import { OnInit } from "@angular/core";
import toastr from 'toastr';

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

    constructor() {}

    public async ngOnInit() {
        toastr.success(`Hello, World!`);
    }

}