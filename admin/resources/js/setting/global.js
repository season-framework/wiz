var setting_builder = function ($scope, $timeout, $sce) {
    $scope.math = Math;
    $scope.trustAsHtml = $sce.trustAsHtml;
    $scope.loaded = true;

    try {
        var properties = JSON.parse(localStorage["season.wiz.resources.properties"]);
        delete properties.root.lastComponentSize;
        $scope.properties = properties;
    } catch (e) {
        $scope.properties = {};
        $scope.properties.root = {};
    }

    $scope.$watch("properties", function () {
        var opt = angular.copy($scope.properties);
        localStorage["season.wiz.resources.properties"] = JSON.stringify(opt);
    }, true);

    $scope.modal = {};
    $scope.modal.config = {};
    $scope.modal.message = function (data) {
        $scope.modal.config = data;
        $timeout();
        $('#modal-message').modal('show');
    };

    $scope.modal.message.hide = function () {
        $scope.modal.config = {};
        $timeout();
        $('#modal-message').modal('hide');
    }

}