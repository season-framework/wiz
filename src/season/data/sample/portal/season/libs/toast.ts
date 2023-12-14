import toastr from 'toastr';

export default class Toast {
    constructor() { }

    public show(message: string, status: string = 'success') {
        if (!toastr[status]) return;
        toastr.options = {
            "closeButton": false,
            "debug": false,
            "newestOnTop": true,
            "progressBar": false,
            "positionClass": "toast-top-right",
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
        toastr[status](message);
    }

    public success(message: string) {
        this.show(message, 'success');
    }

    public error(message: string) {
        this.show(message, 'error');
    }

    public info(message: string) {
        this.show(message, 'info');
    }

    public warning(message: string) {
        this.show(message, 'warning');
    }
}