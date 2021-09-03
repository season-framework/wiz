var shortcutjs = function (element, config) {
    return new (function () {
        var self = this;

        self.holdings = {};
        var ismac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        self.translate = {
            'meta': ismac ? 'control' : 'meta',
            'control': ismac ? 'meta' : 'control',
            'shift': 'shift',
            'alt': 'alt'
        };

        if (!config) config = {};

        self.shortcut = {};

        self.set_shortcut = function (name, fn) {
            name = name.toLowerCase();
            name = name.split('|');
            for (var i = 0; i < name.length; i++) {
                _name = name[i].replace(/  /gim, ' ').trim().split(' ');
                _name.sort();
                _name = _name.join(' ');
                self.shortcut[_name] = fn;
            }
        }

        for (var name in config) {
            self.set_shortcut(name, config[name]);
        }

        $(element).keydown(function (ev) {
            var keyname = ev.key.toLowerCase();
            if (!self.translate[keyname]) {
                self.holdings = {};
                self.holdings[keyname] = true;
            }

            var keynamespace = [];
            for (var key in self.holdings) keynamespace.push(key);
            for (var key in self.translate) {
                if (ev[key + 'Key']) {
                    keynamespace.push(self.translate[key]);
                }
            }

            keynamespace.sort();
            var keylens = keynamespace.length;
            keynamespace = keynamespace.join(' ');
            if (self.shortcut[keynamespace]) {
                self.shortcut[keynamespace](ev, keynamespace);
                self.holdings = {};
                ev.proceed = true;
            }

            if (self.shortcut['default']) {
                self.shortcut['default'](ev, keynamespace);
            } else {
                ev.preventDefault();
            }
        });

        $(element).keyup(function (ev) {
            var keyname = ev.key.toLowerCase();
            delete self.holdings[keyname];
        });
    });
}