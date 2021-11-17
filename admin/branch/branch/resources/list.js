var content_controller = function ($sce, $scope, $timeout) {
    let API = {
        checkout: (branch, base) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/create';
            $.post(url, { branch: branch, base: base }, function (res) {
                resolve(res);
            });
        }),
        delete: (branch, working) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/delete';
            $.post(url, { branch: branch, remote: !working }, function (res) {
                resolve(res);
            });
        }),
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };

    $scope.branch = {};
    $scope.branch.id = BRANCH;
    $scope.branch.list = active_branch;
    $scope.branch.stale = stale_branch;

    $scope.modal = {};
    $scope.modal.data = {};
    $scope.modal.create = async () => {
        $scope.modal.data.create = {};
        $scope.modal.data.create.basebranch = BRANCH;
        $('#modal-new-branch').modal('show');
    }

    $scope.modal.delete = async (item) => {
        $scope.modal.data.delete = item;
        $('#modal-delete').modal('show');
    }

    $scope.event = {};

    $scope.event.create = async (branch, base) => {
        if (!branch || !base) return toastr.error("Branch name at least 2 char");
        if (branch.length < 2) return toastr.error("Branch name at least 2 char");
        $scope.loading = true;
        await API.timeout();
        await API.checkout(branch, base);
        location.reload();
    }

    $scope.event.checkout = async (branch) => {
        $scope.loading = true;
        await API.timeout();
        await API.checkout(branch);
        location.reload();
    }

    $scope.event.delete = async () => {
        let branch = $scope.modal.data.delete.name;
        let working = $scope.modal.data.delete.working;
        $scope.loading = true;
        await API.timeout();
        await API.delete(branch, working);
        location.reload();
    }
};