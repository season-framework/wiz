var content_controller = function ($scope, $timeout, $sce) {
    setting_builder($scope, $timeout, $sce);

    // customized
    $scope.event = {};
    $scope.data = {};

    $scope.event.cache_list = function () {
        $.post('/wiz/admin/api/setting/cache/list', {}, function (res) {
            $scope.data.status = res.data;
            $scope.data.status.dev.sort(function(a, b) {
                return b.cachetime.localeCompare(a.cachetime);
            });

            $scope.data.status.prod.sort(function(a, b) {
                return b.cachetime.localeCompare(a.cachetime);
            });

            $timeout();
        });
    }

    $scope.event.cache_list();
};