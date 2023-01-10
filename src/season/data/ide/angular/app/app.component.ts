import { Component, OnInit, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { Service } from '@wiz/service/service';
import pluginJson from '@wiz/libs/plugin.json';

import toastr from "toastr";

toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-top-center",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": 300,
    "hideDuration": 500,
    "timeOut": 1500,
    "extendedTimeOut": 1000,
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
};

@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit, AfterViewInit {

    constructor(
        public service: Service,
        public ref: ChangeDetectorRef
    ) { }

    public async ngOnInit() {
        await this.service.init(this);
        this.service.leftmenu.build(pluginJson.main, pluginJson.sub);
        this.service.rightmenu.build(pluginJson.app, pluginJson.setting);
        this.service.overlay.build(pluginJson.overlay, []);
    }

    public async ngAfterViewInit() {
        let socket = wiz.socket();

        socket.on("connect", async () => {
            socket.emit("join", { id: wiz.branch() });
        });

        socket.on("log", async (data) => {
            this.service.log(data, "server");
        });

        window.addEventListener("beforeunload", function (e) {
            var confirmationMessage = "\o/";
            e.returnValue = confirmationMessage;
            return confirmationMessage;
        });
    }

}
