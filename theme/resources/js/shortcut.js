var shortcutjs = function (element, config) {
    return new (function () {
        var self = this;
        self.holdings = {};
        if (!config) config = {};

        var isMacLike = /(Mac|iPhone|iPod|iPad)/i.test(navigator.platform);
        var KEYMOD = { 'MetaLeft': 'meta', 'MetaRight': 'meta','OSLeft': 'meta', 'OSRight': 'meta', 'ControlLeft': 'ctrl', 'ControlRight': 'ctrl', 'AltLeft': 'alt', 'AltRight': 'alt', 'ShiftLeft': 'shift', 'ShiftRight': 'shift' };
        if (isMacLike) {
            KEYMOD = { 'MetaLeft': 'ctrl', 'MetaRight': 'ctrl', 'OSLeft': 'ctrl', 'OSRight': 'ctrl', 'ControlLeft': 'meta', 'ControlRight': 'meta', 'AltLeft': 'alt', 'AltRight': 'alt', 'ShiftLeft': 'shift', 'ShiftRight': 'shift' };
        }

        self.shortcut = {};

        self.set_shortcut = function (name, fn) {
            name = name.toLowerCase();
            name = name.split('|');
            for (var i = 0; i < name.length; i++) {
                var _name = name[i].replace(/  /gim, ' ').trim().split(' ');
                if (_name == 'default') {
                    self.shortcut[_name] = fn;
                    continue;
                }
                _name.sort();
                _name = _name.join(' ');
                self.shortcut[_name] = fn;
            }
        }

        for (var name in config) {
            self.set_shortcut(name, config[name]);
        }

        $(element).keydown(function (ev) {
            var keycode = ev.code;
            self.holdings[keycode] = true;

            var keynamespace = [];
            for (var key in self.holdings) {
                if (KEYMOD[key]) {
                    keynamespace.push(KEYMOD[key].toLowerCase());
                } else {
                    keynamespace.push(key.toLowerCase());
                }
            }

            keynamespace.sort();
            keynamespace = keynamespace.join(' ');
            keynamespace = keynamespace.toLowerCase();

            if (self.shortcut[keynamespace]) {
                delete self.holdings[keycode];
                self.shortcut[keynamespace](ev, keynamespace);
                ev.proceed = true;
            }

            if (self.shortcut['default']) {
                self.shortcut['default'](ev, keynamespace);
            }
        });

        $(element).keyup(function (ev) {
            var keycode = ev.code;
            if (self.holdings[keycode])
                delete self.holdings[keycode];
        });
    });
}