var content_controller = function ($sce, $scope, $timeout) {
    let API = {
        checkout: (branch, base) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/create';
            $.post(url, { branch: branch, base: base }, function (res) {
                resolve(res);
            });
        }),
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };


    $scope.branch = {};
    $scope.branch.id = BRANCH;
    $scope.branch.list = branches;
    $scope.branch.checkout = async (branch) => {
        $scope.loading = true;
        await API.timeout();
        await API.checkout(branch);
        location.reload();
    }

    $scope.modal = {};
    $scope.modal.data = {};
    $scope.modal.create = async () => {
        $scope.modal.data.create = {};
        $scope.modal.data.create.basebranch = BRANCH;
        $('#modal-new-branch').modal('show');
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
};