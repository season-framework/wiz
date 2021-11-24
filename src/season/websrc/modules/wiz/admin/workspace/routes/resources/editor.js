/*
 * define editor config
 */
const APPMODE = BRANCH + ".route";
const LOCALSTORAGEID = "season.wiz.route.configuration.2";
const APP_URL = "/wiz/admin/workspace/routes/";
const API_URL = "/wiz/admin/workspace/routes/api";
const TABS = ['controller', 'dic', "preview"];
const CODELIST = [
    { id: 'controller', name: 'Controller' },
    { id: 'dic', name: 'Dictionary' },
    { id: 'preview', name: 'Preview' }
];
const CODETYPES = {
    html: ['pug', 'html'],
    js: ['javascript', 'typescript'],
    css: ['less', 'css', 'scss']
};
let LANGSELECTOR = ($scope) => {
    return async (tab) => {
        var obj = $scope.configuration.tab[tab + '_val'];
        if (obj == 'controller') return 'python';
        if (obj == 'dic') return 'json';
        return 'python';
    }
};
let PROPERTY_WATCHER = async ($scope, key) => {
};
let ADDON = async ($scope) => {
    let API = $scope.API;

    API.search_apps = () => new Promise((resolve) => {
        let url = '/wiz/admin/workspace/apps/api/search';
        $.get(url, function (res) {
            resolve(res);
        });
    });

    $scope.mode = "route";
    $scope.extdata = {};
    $scope.extdata.controller = CTRLS;
    $scope.extdata.branch = BRANCH;
    $scope.extdata.branches = BRANCHES;

    $scope.extdata.browse_active = 'route';

    $scope.extdata.change_browse = async (tab) => {
        $scope.extdata.browse_active = tab;
        await API.timeout();
    }

    $scope.extdata.browse_search = async (val) => {
        val = val.toLowerCase();
        for (var i = 0; i < $scope.extdata.apps.length; i++) {
            let searchindex = ['title', 'namespace', 'id', 'route'];
            $scope.extdata.apps[i].hide = true;
            for (let j = 0; j < searchindex.length; j++) {
                try {
                    let key = searchindex[j];
                    let keyv = $scope.extdata.apps[i].package[key].toLowerCase();
                    if (keyv.includes(val)) {
                        $scope.extdata.apps[i].hide = false;
                        break;
                    }
                } catch (e) {
                }
            }
            if (val.length == 0)
                $scope.extdata.apps[i].hide = false;
        }

        await API.timeout();
    }

    $scope.extdata.browse_select = async (item) => {
        let route = $scope.app.data.package.route;
        $scope.app.data.controller = $scope.app.data.controller + "\n" + 'wiz.response.render("' + route + '", "' + item.package.namespace + '")'
        await API.timeout();
    }

    let res = await API.search_apps();
    if (res.code == 200) {
        $scope.extdata.apps = res.data;
    }

}

let PREVIEW_URL = async (app_id) => {
    return "";
}