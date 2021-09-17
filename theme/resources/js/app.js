var app = angular.module(
    'app', ['ngSanitize', 'ui.monaco', 'ui.tinymce']
).directive('ngEnter', function() {
    return function(scope, element, attrs) {
        element.bind('keydown keypress', function(event) {
            if (event.which === 13) {
                scope.$apply(function() {
                    scope.$eval(attrs.ngEnter);
                });
                event.preventDefault();
            }
        });
    };
}).directive('ngDrag', function($compile, $parse) {
    return function(scope, element, attrs) {
        var config = scope.$eval(attrs.ngDrag);
        if (!config) config = {};
        if (!config.onmove)
            config.onmove = function(self, move) {
                self.target().css('left', (self.pos.left + move.x) + 'px');
                self.target().css('top', (self.pos.top + move.y) + 'px');
            };

        var _dragger = draggerjs(element, config);
        _dragger.attrs = attrs;
        _dragger.scope = scope;

        if (!config.draggers) config.draggers = [];
        config.draggers.push(_dragger);
    };
}).directive('compileTemplate', function($compile, $parse) {
    return {
        link: function(scope, element, attr) {
            var parsed = $parse(attr.ngBindHtml);

            function getStringValue() {
                return (parsed(scope) || '').toString();
            }

            // Recompile if the template changes
            scope.$watch(getStringValue, function() {
                $compile(element, null, -9999)(scope); // The -9999 makes it skip directives so that we do not recompile ourselves
            });
        }
    }
});