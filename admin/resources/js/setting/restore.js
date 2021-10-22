var content_controller = function ($scope, $timeout, $sce) {
    setting_builder($scope, $timeout, $sce);

    // customized
    $scope.event = {};
    $scope.data = {};
    $scope.data.restore = {};

    $scope.event.deployment_list = function () {
        $.post('/wiz/admin/api/setting/deploy/list', {}, function (res) {
            $scope.data.history = res.data;
            $timeout();
        });
    }

    $('#import-file').change(function () {
        var fr = new FileReader();
        fr.onload = function () {
            $scope.data.restore.data = fr.result;
            $scope.loaded = false;
            $timeout();
            var pd = angular.copy($scope.data.restore);
            $.post('/wiz/admin/api/setting/deploy/restore', pd, function (res) {
                if (res.code == 200)
                    return location.reload();
                $scope.loaded = true;
                $scope.modal.message({ title: 'Error', message: 'Version Name required', btn_class: "btn-red", btn_title: "Submit", oncancel: $scope.modal.message.hide });
            });

        };
        fr.readAsText($('#import-file').prop('files')[0]);
    });

    $scope.event.restore = function () {
        if (!$scope.data.restore.version_name) {
            $scope.modal.message({ title: 'Error', message: 'Version Name required', btn_class: "btn-red", btn_title: "Submit", oncancel: $scope.modal.message.hide });
            return;
        }

        if ($scope.data.restore.version_name == 'master') {
            $scope.modal.message({
                title: 'Restore Master', message: "Are you sure to restore 'master' version?", btn_class: "btn-red", btn_title: "Restore", oncancel: function () {
                    $('#import-file').click();
                }
            });
        } else {
            $('#import-file').click();
        }

    }

    $scope.event.set_version = function (item) {
        $.post('/wiz/admin/api/setting/deploy/version', { version: item.version }, function (res) {
            location.reload();
        });
    }

    $scope.event.delete = function (item) {
        $scope.modal.message({
            title: 'Delete', message: "Are you sure to delete '" + item.version_name + "' version?", btn_class: "btn-red", btn_title: "Delete", oncancel: function () {
                $scope.loaded = false;
                $timeout();
                $.post('/wiz/admin/api/setting/deploy/delete', { version: item.version }, function (res) {
                    if (res.code == 200)
                        return location.reload();
                    $scope.loaded = true;
                    $scope.modal.message({ title: 'Error', message: 'Version Name required', btn_class: "btn-red", btn_title: "Submit", oncancel: $scope.modal.message.hide });
                });
            }
        });
    }

    $scope.event.deployment_list();
};