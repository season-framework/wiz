'use strict';

angular.module('ui.monaco', [])
    .constant('uiMonacoConfig', {})
    .directive('uiMonaco', uiMonacoDirective);

function uiMonacoDirective($timeout, uiMonacoConfig) {
    return {
        restrict: 'EA',
        require: '?ngModel',
        compile: function compile() {
            return postLink;
        }
    };

    function postLink(scope, iElement, iAttrs, ngModel) {
        var monacoOptions = angular.extend(
            { value: iElement.text() },
            uiMonacoConfig.monaco || {},
            scope.$eval(iAttrs.uiMonaco),
            scope.$eval(iAttrs.uiMonacoOpts)
        );

        ngModel.$render = function () {
            monacoOptions.value = ngModel.$viewValue;
            newMonacoEditor(iElement, monacoOptions, function (editor) {
                configNgModelLink(editor, ngModel, scope);

                scope.$watch(iAttrs.ngShow, function () {
                    editor.layout();
                });

                scope.$on('Monaco', function (event, callback) {
                    if (angular.isFunction(callback)) {
                        callback(editor);
                    } else {
                        throw new Error('the Monaco event requires a callback function');
                    }
                });

                if (angular.isFunction(monacoOptions.onLoad)) {
                    monacoOptions.onLoad(editor);
                }
            });
        };
    }

    function newMonacoEditor(iElement, monacoOptions, cb) {
        iElement.html('');
        require(['vs/editor/editor.main'], function () {
            $(iElement).css("height", "100%");
            $(iElement).html("<div style='height: 100%; width: 100%;'></div>")
            var div = $(iElement).find("div")[0];
            var editor = monaco.editor.create(div, monacoOptions);

            window.onresize = function () {
                editor.layout();
            };

            cb(editor);
        });
    }

    function configNgModelLink(editor, ngModel, scope) {
        if (!ngModel) { return; }

        ngModel.$render = function () {
            var safeViewValue = ngModel.$viewValue || '';
            editor.getModel().setValue(safeViewValue);
        };

        editor.getModel().onDidChangeContent(function (event) {
            var newValue = editor.getValue();
            if (newValue !== ngModel.$viewValue) {
                scope.$evalAsync(function () {
                    ngModel.$setViewValue(newValue);
                });
            }
        });
    }

}
