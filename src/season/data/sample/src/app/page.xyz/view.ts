import { OnInit } from "@angular/core";
import toastr from "toastr";

@directives({
    HighlightDirective: '@wiz/libs/directives/highlight.directive'
})
export class Component implements OnInit {

    public text: string = 'Hello, World!';

    constructor() {
        this.text = `${this.text} this page is '${WizRoute.segment.page}'`;
    }

    public async ngOnInit() {
        // request to app's API
        let { code, data } = await wiz.call("status");
        console.log(code, data);

        // connect to this app's socket
        let socket = wiz.socket();
        socket.on("connect", async () => {
            toastr.success("socket connected");
        });
    }
}
