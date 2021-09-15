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

    $scope.monaco = function (language) {
        var opt = {
            value: '',
            language: language,
            theme: "vs",
            fontSize: 14,
            automaticLayout: true 
        };

        return opt;
    }

    $scope.codemirror = function (language) {
        var opt = {
            lineNumbers: true,
            mode: language,
            lineWrapping: true,
            autoRefresh: true,
            indentWithTabs: false,
            indentUnit: 4,
            foldGutter: true,
            gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
            tabSize: 4,
            insertSoftTab: true,
            viewportMargin: Infinity,
            keyMap: 'sublime'
        };

        return opt;
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
        claer: function () {
            delete localStorage[version];
        }
    };
}

try {
    app.controller('content', content_controller);
} catch (e) {
    app.controller('content', function () { });
}