let content_controller = async ($scope, $timeout, $sce) => {
    _builder($scope, $timeout);

    $scope.trustAsHtml = $sce.trustAsHtml;

    $scope.branch = BRANCH;
    $scope.branches = BRANCHES;

    $scope.change = async (branch) => {
        location.href = "/wiz/admin/workspace/logger/" + branch;
    }

    let ansi_up = new AnsiUp();
    let socket = io("/wiz");

    $scope.socket = {};
    $scope.socket.log = "";
    $scope.socket.clear = async () => {
        $scope.socket.log = "";
        $timeout();
    }

    socket.on("connect", function (data) {
        if (!data) return;
        $scope.socket.id = data.sid;
        socket.emit("join", { id: BRANCH });
    });

    socket.on("log", function (data) {
        data = data.replace(/ /gim, "__SEASONWIZPADDING__");
        data = ansi_up.ansi_to_html(data).replace(/\n/gim, '<br>').replace(/__SEASONWIZPADDING__/gim, '<div style="width: 6px; display: inline-block;"></div>');
        $scope.socket.log = $scope.socket.log + data;
        $timeout(function () {
            var element = $('.debug-messages')[0];
            if (!element) return;
            element.scrollTop = element.scrollHeight - element.clientHeight;
        });
    });

    socket.on("message", function (data) {
        if (data.type == "status") {
            $scope.socket.users = data.users;
            $timeout();
        }
    });


    $scope.shortcut = {};
    $scope.shortcut.configuration = () => {
        return {
            'clear': {
                key: 'Ctrl KeyK',
                fn: async () => {
                    await $scope.socket.clear();
                }
            }
        }
    };

    $scope.shortcut.bind = async () => {
        $(window).unbind();

        let shortcut_opts = {};
        let shortcuts = $scope.shortcut.configuration();
        for (let key in shortcuts) {
            let keycode = shortcuts[key].key;
            let fn = shortcuts[key].fn;
            if (!keycode) continue;
            shortcut_opts[keycode] = async (ev) => {
                ev.preventDefault();
                await fn();
            };
        }

        shortcutjs(window, shortcut_opts);
    }

    window.addEventListener("focus", $scope.shortcut.bind, false);
};