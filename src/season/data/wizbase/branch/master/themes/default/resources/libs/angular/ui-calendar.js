'use strict';

angular.module('ui.calendar', [])
    .directive('uiCalendar', uiCalendarDirective);

function uiCalendarDirective($timeout, uiMonacoConfig) {
    return {
        restrict: 'EA',
        require: '?ngModel',
        compile: function compile() {
            return postLink;
        }
    };

    function postLink(scope, iElement, iAttrs, ngModel) {
        setTimeout(function () {
            flatpickr(iElement, {
                inline: true,
                locale: 'ko'
            });
        }, 500);
    }
}
