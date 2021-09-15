if (!window.season_wiz) {
    var season_wiz = (function () {
        var obj = {};
        obj.__cache__ = {};

        obj.load = function (app_id, wiz_id, namespace) {
            var wiz = {};
            wiz.id = app_id;
            wiz.namespace = namespace;

            wiz.API = {
                url: function (fnname) {
                    if (wiz.options.render == 'webadmin') {
                        return '/wiz/api/' + app_id + '/' + fnname;
                    } else {
                        return '/wiz/api_src/' + app_id + '/' + fnname;
                    }
                },
                function: function (fnname, data, cb, opts) {
                    var _url = wiz.API.url(fnname);
                    var ajax = {
                        url: _url,
                        type: 'POST',
                        data: data
                    };

                    if (opts) {
                        for (var key in opts) {
                            ajax[key] = opts[key];
                        }
                    }

                    $.ajax(ajax).always(function (a, b, c) {
                        if (a.log && API && API.logger) API.logger(a.code, a.log);
                        cb(a, b, c);
                    });
                }
            };

            // self event
            wiz._event = {};
            wiz.bind = function (name, fn) {
                wiz._event[name] = fn;
            };

            wiz.connect = function (id) {
                if (!obj.__cache__[id]) return null;
                var connected_wiz = obj.__cache__[id]
                var _obj = {};
                _obj.event = function (name, cb) {
                    if (!connected_wiz._event[name]) {
                        if (cb) cb();
                        return;
                    }
                    connected_wiz._event[name](_obj._data, cb);
                };
                _obj._data = null;
                _obj.data = function (data) {
                    _obj._data = data;
                    return _obj;
                }
                return _obj;
            }

            obj.__cache__[namespace] = wiz;
            obj.__cache__[wiz_id] = wiz;
            return wiz;
        }

        return obj;
    })();
}

