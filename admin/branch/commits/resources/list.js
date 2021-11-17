var content_controller = function ($sce, $scope, $timeout) {
    $scope.branch = {};
    $scope.branch.id = BRANCH;
    $scope.branch.list = BRANCHES;
    $scope.branch.change = async (branchname) => {
        location.href = location.pathname + "?branch=" + branchname;
    }

    $scope.modal = {};
    $scope.modal.data = {};
    $scope.modal.create = async () => {
        $('#modal-new-branch').modal('show');
    }

};