var content_controller = function ($scope, $timeout, $sce) {
    setting_builder($scope, $timeout, $sce);
    
    $scope.event = {};
    $scope.status = {};
    $scope.data = {};

    $scope.event.build_wiz = function () {
        $scope.loaded = false;
        $timeout();
        $.post('/wiz/admin/api/wiz/build', {}, function (res) {
            $scope.loaded = true;
            $timeout();
        });
    }

    $scope.data.backup = "master";
};