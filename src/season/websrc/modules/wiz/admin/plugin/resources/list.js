var content_controller = async ($sce, $scope, $timeout) => {
    _builder($scope, $timeout);
    setting_builder($scope, $timeout, $sce);

    let API = {
        handler: (resolve, reject) => async (res) => {
            if (res.code == 200) resolve(res.data);
            else reject(res);
        },
        list: () => new Promise((resolve, reject) => {
            let url = '/wiz/admin/plugin/api/list';
            $.get(url, API.handler(resolve, reject));
        }),
        create: (data) => new Promise((resolve, reject) => {
            let url = '/wiz/admin/plugin/api/create';
            data = angular.copy(data);
            $.post(url, data, resolve);
        }),
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };

    $scope.math = Math;

    $scope.list = [];
    $scope.event = {};

    $scope.event.load = async () => {
        let data = await API.list();

        $scope.list = data;
        $scope.list.sort((a, b) => {
            let comp = 0;
            try {
                comp = a.name.localeCompare(b.name);
                if (comp != 0) return comp;
            } catch (e) { }
            comp = a.id.localeCompare(b.id);
            return comp;
        });

        await API.timeout();
    }

    $scope.event.search = async (val) => {
        val = val.toLowerCase();
        for (var i = 0; i < $scope.list.length; i++) {
            if (val.length == 0) {
                $scope.list[i].hide = false;
                continue;
            }
                
            let searchindex = ['name', 'id', 'author_name'];
            $scope.list[i].hide = true;
            for (let j = 0; j < searchindex.length; j++) {
                try {
                    let key = searchindex[j];
                    let keyv = $scope.list[i][key].toLowerCase();
                    if (keyv.includes(val)) {
                        $scope.list[i].hide = false;
                        break;
                    }
                } catch (e) {
                }
            }
        }

        $timeout();
    }

    $scope.modal = {};
    $scope.modal.data = {};
    $scope.modal.create = async () => {
        $scope.modal.data.create = {};
        $('#modal-create').modal('show');
    }

    $scope.event.create = async () => {
        let pd = angular.copy($scope.modal.data.create);
        let res = await API.create(pd);

        if(res.code == 200 ) {
            location.reload();
        } else {
            toastr.error(res.data);
        }
    };


    $scope.event.change_id = async (val) => {
        $scope.modal.data.create.name = val;
        await API.timeout();
    };

    $scope.event.load();
};