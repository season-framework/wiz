var content_controller = async ($scope, $timeout, $sce) => {
    _builder($scope, $timeout);
    setting_builder($scope, $timeout, $sce);

    const API = {
        handler: (resolve, reject) => async (res) => {
            if (res.code == 200) resolve(res.data);
            else reject(res);
        },
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        }),
        info: () => new Promise((resolve, reject) => {
            $.post('/wiz/admin/setting/api/config/packageinfo', {}, API.handler(resolve, reject));
        }),
        update: (data) => new Promise((resolve, reject) => {
            $.post('/wiz/admin/setting/api/config/update', { data: JSON.stringify(data, null, 4) }, API.handler(resolve, reject));
        }),
        clean: () => new Promise((resolve, reject) => {
            $.get('/wiz/admin/setting/api/config/clean', API.handler(resolve, reject));
        }),
        apply: () => new Promise((resolve, reject) => {
            $.post('/wiz/admin/setting/api/config/apply', {}, API.handler(resolve, reject));
        })
    };

    $scope.monaco_properties = $scope.monaco("python");
    $scope.monaco_properties.minimap = {
        enabled: false
    };

    $scope.status = {};
    $scope.themes = themes;
    $scope.data = await API.info();

    $scope.event = {};

    $scope.event.update = async () => {
        let data = angular.copy($scope.data);
        try {
            await API.update(data);
            toastr.success("Saved");
        } catch (e) {
            toastr.error(e.data);
        }
    }

    $scope.event.apply = async () => {
        let data = angular.copy($scope.data);
        try {
            await API.update(data);
            await API.apply();
            toastr.success("Applied");
        } catch (e) {
            toastr.error(e.data);
        }
    }

    $scope.event.clean = async () => {
        try {
            await API.clean();
            toastr.success("Cleaned");
        } catch (e) {
            toastr.error(e.data);
        }
    }

    let shortcuts = async () => {
        $(window).unbind();
        shortcutjs(window, {
            'Ctrl KeyS': async (ev) => {
                $scope.event.update();
                ev.preventDefault();
            }
        });
    }

    shortcuts();
    window.addEventListener("focus", shortcuts, false);

    await API.timeout();
};