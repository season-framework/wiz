import $ from "jquery";

export default class Request {
    constructor() { }

    public async post(url: string, data: any = {}) {
        let request = () => {
            return new Promise((resolve) => {
                $.ajax({
                    url: url,
                    type: "POST",
                    data: data
                }).always(function (res) {
                    resolve(res);
                });
            });
        }

        return await request();
    }

}