var draggerjs = function (element, config) {
    return new (function () {
        var self = this;

        if (!config) config = {};
        if (!config.container) config.container = 'body';
        if (!config.target) config.target = element;
        if (config.onstart) self._start = config.onstart;
        if (config.onmove) self._move = config.onmove;
        if (config.onend) self._end = config.onend;

        self.config = config;
        self.element = element;
        self.mode = 'stop';
        self.start_ev = null;
        self.pos = {};
        self.counter = 0;

        element.bind('mousedown', function (ev) {
            try {
                self.pos = {}
                self.pos.top = self.target().css('top').replace('px', '') * 1;
                self.pos.left = self.target().css('left').replace('px', '') * 1;
                self.pos.bottom = self.target().css('bottom').replace('px', '') * 1;
                self.pos.right = self.target().css('right').replace('px', '') * 1;

                self.mode = 'start';
                self.start_event = ev;
                self.event = ev;
                self.counter = 0;
                if (self._start) self._start(self);
            } catch (e) {
                self.mode = 'stop';
            }
        });

        $(self.config.container).mousemove(function (ev) {
            if (self.mode == 'stop') return;
            start_ev = self.start_event;
            self.event = ev
            var move_x = ev.clientX - start_ev.clientX;
            var move_y = ev.clientY - start_ev.clientY;
            self.counter = self.counter + 1;
            if (self._move) self._move(self, { x: move_x, y: move_y });
        });

        $(window).bind('mouseup', function (ev) {
            if (self.mode == 'stop') return;
            self.mode = 'stop';
            start_ev = self.start_event;
            var move_x = ev.clientX - start_ev.clientX;
            var move_y = ev.clientY - start_ev.clientY;
            self.start_event = null;
            self.event = ev;
            if (self._end) self._end(self, { x: move_x, y: move_y });
        })

        this.target = function () {
            if (self.config.target)
                return $(self.config.target);
            return $(self.element);
        }

        this.onstart = function (cb) {
            self._start = cb;
            return self;
        }

        this.onmove = function (cb) {
            self._move = cb;
            return self;
        }

        this.onend = function (cb) {
            self._end = cb;
            return self;
        }

        this.stop = function () {
            self.mode = 'stop';
        }

        return this;
    })();
};