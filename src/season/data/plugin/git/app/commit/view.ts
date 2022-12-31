import { OnInit } from '@angular/core';
import { Service } from '@wiz/service/service';

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

export class Component implements OnInit {
    public APP_ID: string = wiz.namespace;
    public loading: boolean = true;

    public files: any = { staged: [], unstaged: [] };
    public message: string = '';

    constructor(private service: Service) {
    }

    public async ngOnInit() {
        await this.changes();

        this.service.editor.bind('updated', async () => {
            await this.changes();
        });

        await this.add();
    }

    public async loader(status) {
        this.loading = status;
        await this.service.render();
    }

    public async reset(file: string | null = null) {
        await this.loader(true);
        await wiz.call("reset", { file: file });
        await this.changes();
    }

    public async add(file: string | null = null) {
        await this.loader(true);
        await wiz.call("add", { file: file });
        await this.changes();
    }

    public async commit(message: string) {
        await this.loader(true);
        let { code } = await wiz.call("commit", { message });
        if (code == 200) toastr.success("Committed");
        await this.changes();
    }

    public async changes() {
        await this.loader(true);
        let { data } = await wiz.call("changes");

        let parser = (data) => {
            for (let i = 0; i < data.length; i++) {
                data[i].color = 'bg-secondary';
                if (data[i].change_type == 'M')
                    data[i].color = 'bg-yellow';
                if (data[i].change_type == 'R')
                    data[i].color = 'bg-yellow';
                if (data[i].change_type == 'D')
                    data[i].color = 'bg-red';
                if (data[i].change_type == 'A')
                    data[i].color = 'bg-green';
            }
            return data;
        }

        data.staged = parser(data.staged);
        data.unstaged = parser(data.unstaged);

        this.files = data;
        await this.loader(false);
    }
}