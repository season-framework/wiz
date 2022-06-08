window.season_wiz = (() => {
    let obj = {};
    obj.__cache__ = {};

    obj.load = (app_id, namespace, render_id) => {
        let wiz = {};
        wiz.id = app_id;
        wiz.namespace = namespace;
        wiz.render_id = render_id;

        wiz.socket = {};
        wiz.socket.active = false;
        wiz.url = "{$URL$}";

        if (window.io) {
            wiz.socket.active = true;
            wiz.socket.get = (socketnamespace) => {
                let socketns = "{$SOCKETBASEPATH$}" + "/" + app_id;
                if (socketnamespace) socketns = "{$SOCKETBASEPATH$}" + "/" + socketnamespace;
                wiz.socket_instance = window.io(socketns);
                return wiz.socket_instance;
            }
        }

        wiz.API = {
            url: (fnname) => '{$BASEPATH$}/' + app_id + '/' + fnname,
            function: (fnname, data, cb, opts) => {
                let _url = wiz.API.url(fnname);
                let ajax = {
                    url: _url,
                    type: 'POST',
                    data: data
                };

                if (opts) {
                    for (let key in opts) {
                        ajax[key] = opts[key];
                    }
                }

                $.ajax(ajax).always((a, b, c) => {
                    cb(a, b, c);
                });
            },
            async: (fnname, data, opts = {}) => {
                const _url = wiz.API.url(fnname);
                let ajax = {
                    url: _url,
                    type: "POST",
                    data: data,
                    ...opts,
                };

                return new Promise((resolve) => {
                    $.ajax(ajax).always(function (a, b, c) {
                        resolve(a, b, c);
                    });
                });
            }
        };

        wiz.timeout = (timestamp) => new Promise((resolve) => {
            setTimeout(resolve, timestamp);
        });

        wiz._event = {};
        wiz._response = {};
        wiz._response_activator = {};

        wiz.bind = (name, fn, err = true) => {
            wiz._event[name] = (data) => new Promise(async (resolve, reject) => {
                let res = await fn(data);
                if (res) {
                    return resolve(res);
                }

                wiz._response_activator[name] = true;

                let response_handler = () => {
                    // if not activate, stop loop
                    if (!wiz._response_activator[name]) {
                        if (err) reject("deprecated event `" + name + "` of `" + wiz.namespace + "`");
                        return;
                    }

                    // if activate 
                    if (name in wiz._response) {
                        let resp = wiz._response[name];
                        delete wiz._response[name];
                        delete wiz._response_activator[name];
                        resolve(resp);
                        return;
                    }

                    setTimeout(response_handler, 100);
                }
                response_handler();
            });
            return wiz;
        };

        wiz.response = (name, data) => {
            if (!wiz._response_activator[name]) return;
            wiz._response[name] = data;
            return wiz;
        }

        wiz.connect = (id) => {
            if (!obj.__cache__[id]) return null;
            let connected_wiz = obj.__cache__[id];
            let _obj = {};

            _obj.event = async (name) => {
                delete connected_wiz._response_activator[name];
                await wiz.timeout(200);

                if (connected_wiz._event[name]) {
                    let res = await connected_wiz._event[name](_obj._data);
                    return res;
                }
                return null;
            };

            _obj._data = null;
            _obj.data = (data) => {
                _obj._data = data;
                return _obj;
            }
            return _obj;
        }

        obj.__cache__[namespace] = wiz;
        obj.__cache__[app_id] = wiz;

        return wiz;
    }

    return obj;
})();