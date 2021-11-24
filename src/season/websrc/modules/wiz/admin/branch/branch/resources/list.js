var content_controller = async ($sce, $scope, $timeout) => {
    let API = {
        list: () => new Promise((resolve, reject) => {
            let url = '/wiz/admin/branch/branch/api/list';
            $.get(url, function (res) {
                if (res.code == 200) resolve(res.data);
                else reject(res);
            });
        }),
        checkout: (data) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/create';
            data = angular.copy(data);
            $.post(url, data, function (res) {
                resolve(res);
            });
        }),
        pull_request: (data) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/pull_request';
            data = angular.copy(data);
            $.post(url, data, function (res) {
                resolve(res);
            });
        }),
        delete: (branch, working) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/delete';
            $.post(url, { branch: branch, remote: !working }, function (res) {
                resolve(res);
            });
        }),
        delete_request: (branch, base) => new Promise((resolve) => {
            let url = '/wiz/admin/branch/branch/api/delete_request';
            $.post(url, { branch: branch, base_branch: base }, function (res) {
                resolve(res);
            });
        }),
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };

    $scope.loading = true;

    $scope.branch = {};
    $scope.branch.id = BRANCH;

    let branches = await API.list();
    $scope.branch.list = branches.active;
    $scope.branch.stale = branches.stale;
    $scope.branch.pull_request = branches.pull_request;

    $scope.modal = {};
    $scope.modal.data = {};
    $scope.modal.create = async () => {
        $scope.modal.data.create = {};
        $scope.modal.data.create.base_branch = BRANCH;
        $scope.modal.data.create.name = author.name;
        $scope.modal.data.create.email = author.email;
        $('#modal-new-branch').modal('show');
    }

    $scope.modal.commiter = async (item) => {
        console.log(item);
        $scope.modal.data.commiter = {};
        $scope.modal.data.commiter.branch = item.name;
        $scope.modal.data.commiter.name = item.author.name;
        $scope.modal.data.commiter.email = item.author.email;
        $('#modal-change-commiter').modal('show');
    }

    $scope.modal.merge = async (item) => {
        $scope.modal.data.merge = {};
        $scope.modal.data.merge.branch = item.name;
        $scope.modal.data.merge.name = item.author.name;
        $scope.modal.data.merge.email = item.author.email;
        $('#modal-merge-branch').modal('show');
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
        $scope.modal.data.create.branch = branch;
        $scope.modal.data.create.base_branch = base;
        let create = angular.copy($scope.modal.data.create);
        await API.timeout();
        let res = await API.checkout(create);
        if (res.code != 200) {
            $scope.loading = false;
            await API.timeout();
            return toastr.error(res.data);
        }
        location.reload();
    }

    $scope.event.pull_request = async (branch, base) => {
        if (!branch || !base) return toastr.error("Branch not selected");
        if (branch == base) return toastr.error("Select different branch");
        $scope.loading = true;
        $scope.modal.data.merge.branch = branch;
        $scope.modal.data.merge.base_branch = base;
        let merge = angular.copy($scope.modal.data.merge);
        await API.timeout();
        let res = await API.pull_request(merge);
        if (res.code != 200) {
            $scope.loading = false;
            await API.timeout();
            return toastr.error(res.data);
        }
        location.reload();
    }


    $scope.event.checkout = async (branch) => {
        $scope.loading = true;
        let checkout_object = {};
        checkout_object.branch = branch;
        await API.timeout();
        let res = await API.checkout(checkout_object);
        if (res.code != 200) {
            $scope.loading = false;
            await API.timeout();
            return toastr.error(res.data);
        }
        location.reload();
    }

    $scope.event.change_commiter = async (branch) => {
        $scope.loading = true;
        $scope.modal.data.commiter.branch = branch;
        let create = angular.copy($scope.modal.data.commiter);
        await API.timeout();
        let res = await API.checkout(create);
        if (res.code != 200) {
            $scope.loading = false;
            await API.timeout();
            return toastr.error(res.data);
        }
        location.reload();
    }


    $scope.event.delete = async () => {
        if ($scope.modal.data.delete.from) {
            let branch = $scope.modal.data.delete.from;
            let base_branch = $scope.modal.data.delete.to;
            $scope.loading = true;
            await API.timeout();
            await API.delete_request(branch, base_branch);
        } else {
            let branch = $scope.modal.data.delete.name;
            let working = $scope.modal.data.delete.working;
            $scope.loading = true;
            await API.timeout();
            await API.delete(branch, working);
        }

        location.reload();
    }

    $scope.loading = false;
    await API.timeout();
};