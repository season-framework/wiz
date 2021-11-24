var content_controller = async ($sce, $scope, $timeout) => {
    $scope.hash = location.hash.split("#")[1];
    if (!$scope.hash) $scope.hash = '';

    let API = {
        handler: (resolve, reject) => async (res) => {
            if (res.code == 200) resolve(res.data);
            else reject(res);
        },
        load: () => new Promise((resolve, reject) => {
            let url = '/wiz/admin/workspace/apps/api/search';
            $.get(url, API.handler(resolve, reject));
        }),

        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };

    $scope.math = Math;

    $scope.list = [];
    $scope.facet = {};
    $scope.facet.category = {};
    $scope.event = {};
    $scope.categoires = CATEGORIES;

    $scope.event.category = async (hash) => {
        location.href = location.href.split("#")[0] + "#" + hash;
        $scope.hash = hash;

        for (var i = 0; i < $scope.list.length; i++) {
            let searchindex = ['category'];
            $scope.list[i].hide = true;
            for (let j = 0; j < searchindex.length; j++) {
                try {
                    let key = searchindex[j];
                    let keyv = $scope.list[i].package[key].toLowerCase();
                    if (keyv == hash) {
                        $scope.list[i].hide = false;
                        break;
                    }
                } catch (e) {
                }
            }
            if (hash.length == 0)
                $scope.list[i].hide = false;
        }

        await API.timeout();
    }

    $scope.event.load = async () => {
        $scope.list = await API.load();

        for (let i = 0; i < $scope.list.length; i++) {
            let category = $scope.list[i].package.category;
            if (!$scope.facet.category[category]) $scope.facet.category[category] = 0;
            $scope.facet.category[category]++;
        }
        $scope.facet.count = $scope.list.length;

        $scope.list.sort((a, b) => {
            let comp = 0;
            comp = a.package.namespace.localeCompare(b.package.namespace);
            return comp;
        });

        await API.timeout();
    }

    $scope.event.search = async (val) => {
        val = val.toLowerCase();
        for (var i = 0; i < $scope.list.length; i++) {
            let searchindex = ['title', 'namespace', 'route'];
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

    await $scope.event.load();
    await $scope.event.category($scope.hash);
};