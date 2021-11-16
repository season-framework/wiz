let content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);

    $scope.configuration = {};       // state data for maintaining ui
    $scope.tree = {};
    $scope.viewer = {};
    $scope.shortcut = {};
    $scope.loading = {};
    $scope.modal = {};

    /*
     * define variables
     */
    let BUILDER = {};

    let API = {
        load: (item) => new Promise((resolve) => {
            let url = API_URL + '/tree';
            $.post(url, { path: item.path, name: item.name, type: item.type }, function (res) {
                resolve(res);
            });
        }),
        upload: (data, xhr) => new Promise((resolve) => {
            let url = API_URL + '/upload';
            $.ajax({
                url: url,
                type: 'POST',
                xhr: xhr,
                data: data,
                cache: false,
                contentType: false,
                processData: false
            }).always(function (res) {
                resolve(res);
            });
        }),
        update: (data) => new Promise((resolve) => {
            let url = API_URL + '/update';
            $.post(url, data, function (res) {
                resolve(res);
            });
        }),
        delete: (data) => new Promise((resolve) => {
            let url = API_URL + '/delete';
            $.post(url, data, function (res) {
                resolve(res);
            });
        }),
        delete_bulk: (data) => new Promise((resolve) => {
            let url = API_URL + '/delete_bulk';
            $.post(url, { data: JSON.stringify(data) }, function (res) {
                resolve(res);
            });
        }),
        rename: (data) => new Promise((resolve) => {
            let url = API_URL + '/rename';
            $.post(url, data, function (res) {
                resolve(res);
            });
        }),
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };


    /* 
     * load wiz editor options from localstorage
     */
    try {
        let configuration = JSON.parse(localStorage[LOCALSTORAGEID]);
        delete configuration.root.lastComponentSize;
        $scope.configuration = configuration;
    } catch (e) {
        $scope.configuration = {};
        $scope.configuration.root = {};
    }

    $scope.$watch("configuration", function () {
        let configuration = angular.copy($scope.configuration);
        localStorage[LOCALSTORAGEID] = JSON.stringify(configuration);
    }, true);


    BUILDER.tree = async () => {
        $scope.tree.data = TREE_DATA;

        $scope.tree.init = async () => {
            for (let i = 0; i < $scope.tree.data.length; i++) {
                let item = $scope.tree.data[i];
                if (item.type == "folder" && !item.sub) {
                    await $scope.tree.load(item);
                }
            }
        }

        $scope.tree.load = async (item) => {
            console.log(item);
        };
    }

    BUILDER.viewer = async () => {

    }

    /*
     * define loading
     */
    BUILDER.loading = async () => {
        $scope.loading.status = true;
        $scope.loading.show = async () => {
            $scope.loading.status = true;
            await API.timeout();
        }

        $scope.loading.hide = async () => {
            $scope.loading.status = false;
            await API.timeout();
        }
    }

    /*
     * define modal events
     */

    BUILDER.modal = async () => {
        $scope.modal.delete = async () => {
            $('#modal-delete').modal('show');
        }
    }

    BUILDER.init = async () => {
        await $scope.tree.init();
    }


    BUILDER.tree();
    BUILDER.loading();
    BUILDER.modal();
    BUILDER.init();
};