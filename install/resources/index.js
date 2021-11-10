var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);

    $scope.monaco_properties = $scope.monaco("python");
    $scope.monaco_properties.minimap = {
        enabled: false
    };

    $scope.data = {
        framework: {
            host: "0.0.0.0",
            port: "3000",
            log_level: "2",
            secret_key: "",
            dev: "True",
            watch: {
                pattern: "*",
                ignore: "websrc/wiz.json"
            },
            filter: "request_uri = framework.request.uri()\nif request_uri == '/':\n    return framework.response.redirect('/wiz')"
        },
        wiz: {
            category: "component: Component\nwidget: Widget\nmodal: Modal",
            topmenus: "HOME: /\nWIZ: /wiz",
            acl: "def acl(framework):\n    req_ip = framework.request.client_ip()\n    if req_ip not in ['127.0.0.1', '" + request_ip + "']:\n        framework.response.abort(401)"
        }
    };

    var steps = [];
    steps.push({ id: "start" });
    steps.push({ id: "framework.default", });
    steps.push({ id: "framework.watch" });
    steps.push({ id: "wiz.category" });
    steps.push({ id: "wiz.acl", wide: true });
    steps.push({ id: "filter", wide: true });

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
                location.href = window.location.protocol + "//" + window.location.hostname + ":" + $scope.data.framework.port;
            }, 3000);
        });
    }
};
