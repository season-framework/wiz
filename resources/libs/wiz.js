var season_wiz = function (app_id) {
    var obj = {}
    obj.API = {
        url: function (fnname) {
            if (obj.options.render == 'webadmin') {
                return '/wiz/api/' + app_id + '/' + fnname;
            } else {
                return '/wiz/api_src/' + app_id + '/' + fnname;
            }
        },
        function: function (fnname, data, cb, opts) {
            var _url = obj.API.url(fnname);
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

    return obj;
};
