var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);
    setting_builder($scope, $timeout, $sce);

    $scope.monaco_properties = $scope.monaco("python");
    $scope.monaco_properties.minimap = {
        enabled: false
    };

    $scope.event = {};
    $scope.status = {};
    $scope.data = {};
    $scope.themes = themes;

    $.post('/wiz/admin/setting/api/config/packageinfo', {}, function (res) {
        $scope.data = res.data;
        $timeout();
    });

    $scope.event.save = function () {
        var data = angular.copy($scope.data);
        $.post('/wiz/admin/setting/api/config/update', { data: JSON.stringify(data, null, 4) }, function (res) {
            toastr.success("Saved");
        });
    }

    function shortcuts() {
        $(window).unbind();
        shortcutjs(window, {
            'Ctrl KeyS': function (ev) {
                $scope.event.save();
                ev.preventDefault();
            }
        });
    }

    shortcuts();
    window.addEventListener("focus", shortcuts, false);

    $scope.event.apply = function () {
        var data = angular.copy($scope.data);
        $.post('/wiz/admin/setting/api/config/update', { data: JSON.stringify(data, null, 4) }, function (res) {
            $.post('/wiz/admin/setting/api/config/apply', {}, function (res) {
                if (res.code == 200) {
                    return toastr.success("Applied");
                }
                return toastr.error(res.data);
            });
        });
    }
};