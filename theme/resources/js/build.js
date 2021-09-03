var json_array_parse = function (val, defaultvalue) {
    try {
        return JSON.parse(val);
    } catch (e) {
        if (defaultvalue)
            return defaultvalue;
    }
    return val;
}

var _builder = function ($scope, $timeout) {
    $scope.modal = {};
    $scope.modal.alert = function (message) {
        $scope.modal.color = 'btn-danger';
        $scope.modal.message = message;
        $('#modal-alert').modal('show');
        $timeout();
    }

    $scope.modal.success = function (message) {
        $scope.modal.color = 'btn-primary'
        $scope.modal.message = message;
        $('#modal-alert').modal('show');
        $timeout();
    }

    $scope.codemirror = function (language) {
        return {
            lineNumbers: true,
            mode: language,
            autoRefresh: true,
            indentWithTabs: false,
            tabSize: 4,
            viewportMargin: Infinity,
            keyMap: 'sublime'
        };
    }
}

var cache_builder = function (version) {
    return {
        get: function (_default) {
            return json_array_parse(localStorage[version], _default);
        },
        update: function (value) {
            localStorage[version] = JSON.stringify(angular.copy(value));
        },
        claer: function() {
            delete localStorage[version];
        }
    };
}

try {
    app.controller('content', content_controller);
} catch (e) {
    app.controller('content', function() {});
}