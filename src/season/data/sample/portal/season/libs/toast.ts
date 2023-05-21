import toastr from 'toastr';
toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-bottom-center",
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

export default class Toast {
    constructor() { }

    public show(message: string, status: string = 'success') {
        if (!toastr[status]) return;
        toastr[status](message);
    }

    public success(message: string) {
        toastr.success(message);
    }

    public error(message: string) {
        toastr.error(message);
    }

    public info(message: string) {
        toastr.info(message);
    }

    public warning(message: string) {
        toastr.warning(message);
    }
}