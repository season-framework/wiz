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
    $scope.mode = "route";
    $scope.extdata = {};
    $scope.extdata.controller = CTRLS;
    $scope.extdata.branch = BRANCH;
    $scope.extdata.branches = BRANCHES;
}
let PREVIEW_URL = async (app_id) => {
    return "";
}