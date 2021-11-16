var content_controller = function ($sce, $scope, $timeout) {
    var API = {
        SEARCH: '/wiz/admin/workspace/routes/api/search'
    };

    $scope.category = {
        widget: "위젯"
    };

    $scope.math = Math;

    $scope.list = [];
    $scope.event = {};

    $scope.event.load = function () {
        var pd = angular.copy($scope.search);
        $.post(API.SEARCH, pd, function (res) {
            if (res.code == 200) {
                $scope.list = res.data;
            }
            $timeout();
        })
    }

    $scope.event.search = async (val) => {
        val = val.toLowerCase();
        for (var i = 0; i < $scope.list.length; i++) {
            let searchindex = ['title', 'namespace', 'route', 'category'];
            $scope.list[i].hide = true;
            for (let j = 0; j < searchindex.length; j++) {
                try {
                    let key = searchindex[j];
                    let keyv = $scope.list[i].package[key].toLowerCase();
                    if (keyv.includes(val)) {
                        $scope.list[i].hide = false;
                        break;
                    }
                } catch (e) {
                }
            }
            if (val.length == 0)
                $scope.list[i].hide = false;
        }

        $timeout();
    }

    $scope.event.load();
};