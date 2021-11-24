var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);

    $scope.monaco_properties = $scope.monaco("python");
    $scope.monaco_properties.minimap = {
        enabled: false
    };

    $scope.data = wizpackage;

    console.log(wizpackage);

    var steps = [];
    steps.push({ id: "start" });
    steps.push({ id: "framework.default", });
    steps.push({ id: "wiz.category" });
    steps.push({ id: "wiz.acl", wide: true });

    $scope.steps = steps;
    $scope.step = $scope.steps[0];
    $scope.step_index = 1;

    $scope.islast = false;
    $scope.isfirst = true;

    $scope.event = {};
    $scope.event.next = function () {
        var current_index = $scope.steps.indexOf($scope.step);
        current_index = current_index + 1;
        if (current_index > $scope.steps.length - 1) return;
        if (current_index == $scope.steps.length - 1) $scope.islast = true;
        $scope.isfirst = false;
        $scope.step = $scope.steps[current_index];
        $scope.step_index = current_index + 1;
        $timeout();
    }

    $scope.event.prev = function () {
        var current_index = $scope.steps.indexOf($scope.step);
        current_index = current_index - 1;
        if (current_index < 0) return;
        if (current_index == 0) $scope.isfirst = true;
        $scope.islast = false;
        $scope.step = $scope.steps[current_index];
        $scope.step_index = current_index + 1;
        $timeout();
    }

    $scope.event.build = function () {
        var pd = angular.copy($scope.data);
        pd = JSON.stringify(pd);
        $.post("/wiz/install/build", { data: pd }, function (res) {
            $timeout(function () {
                location.href = window.location.protocol + "//" + window.location.hostname + ":" + $scope.data.framework.port + "/wiz";
            }, 3000);
        });
    }
};
