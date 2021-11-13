var content_controller = function ($sce, $scope, $timeout) {
    var API = {
        SEARCH: '/wiz/admin/packages/routes/api/search'
    };

    $scope.category = {
        widget: "위젯"
    };

    $scope.math = Math;

    $scope.list = [];
    $scope.event = {};

    $scope.event.load = function () {
        var pd = angular.copy($scope.search);
        $.post(API.SEARCH, pd, function (res) {
            if (res.code == 200) {
                $scope.list = res.data;
            }
            $timeout();
        })
    }

    $scope.event.search = function () {
        $scope.search.page = 1;
        var q = Object.entries(angular.copy($scope.search)).map(e => e.join('=')).join('&');
        location.href = "?" + q;
    }

    $scope.event.load();
};