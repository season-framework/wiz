import $ from "jquery";
import { io } from "socket.io-client";

export default class Wiz {
    namespace: any;
    baseuri: any;

    constructor(baseuri: any) {
        this.baseuri = baseuri;
    }

    public app(namespace: any) {
        let instance = new Wiz(this.baseuri);
        instance.namespace = namespace;
        return instance;
    }

    public dev() {
        let findcookie = (name) => {
            let ca: Array<string> = document.cookie.split(';');
            let caLen: number = ca.length;
            let cookieName = `${name}=`;
            let c: string;

            for (let i: number = 0; i < caLen; i += 1) {
                c = ca[i].replace(/^\s+/g, '');
                if (c.indexOf(cookieName) == 0) {
                    return c.substring(cookieName.length, c.length);
                }
            }
            return '';
        }

        let isdev = findcookie("season-wiz-devmode");
        if (isdev == 'true') return true;
        return false;
    }

    public project() {
        let findcookie = (name) => {
            let ca: Array<string> = document.cookie.split(';');
            let caLen: number = ca.length;
            let cookieName = `${name}=`;
            let c: string;

            for (let i: number = 0; i < caLen; i += 1) {
                c = ca[i].replace(/^\s+/g, '');
                if (c.indexOf(cookieName) == 0) {
                    return c.substring(cookieName.length, c.length);
                }
            }
            return '';
        }

        let project = findcookie("season-wiz-project");
        if (project) return project;
        return "main";
    }

    public socket() {
        let socketns = this.baseuri;
        if (this.namespace)
            socketns = socketns + "/" + this.namespace;
        return io(socketns);
    };

    public url(function_name: string) {
        if (function_name[0] == "/") function_name = function_name.substring(1);
        return this.baseuri + "/api/" + this.namespace + "/" + function_name;
    }

    public call(function_name: string, data = {}, options = {}) {
        let ajax = {
            url: this.url(function_name),
            type: "POST",
            data: data,
            ...options
        };

        return new Promise((resolve) => {
            $.ajax(ajax).always(function (res) {
                resolve(res);
            });
        });
    }

}