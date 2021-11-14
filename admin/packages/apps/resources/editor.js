/*
 * define editor config
 */
const APPMODE = BRANCH + ".app";
const LOCALSTORAGEID = "season.wiz.app.configuration";
const APP_URL = "/wiz/admin/packages/apps/";
const API_URL = "/wiz/admin/packages/apps/api";
const TABS = ['controller', 'api', 'socketio', 'html', 'js', 'css', 'dic', "preview"];
const CODELIST = [
    { id: 'controller', name: 'Controller' },
    { id: 'api', name: 'API' },
    { id: 'socketio', name: 'Socket API' },
    { id: 'html', name: 'HTML' },
    { id: 'js', name: 'JS' },
    { id: 'css', name: 'CSS' },
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
        if (obj == 'dic') return 'json';
        if ($scope.app.data.package.properties[obj])
            return $scope.app.data.package.properties[obj];
        return 'python';
    }
};
let PROPERTY_WATCHER = async ($scope, key) => {
    for (let targettab in $scope.app.editor.properties) {
        if ($scope.configuration.tab[targettab + "_val"] == key) {
            await $scope.app.editor.code.change(targettab, key);
        }
    }
};
let ADDON = async ($scope) => {
    $scope.extdata = {};
    $scope.extdata.controller = CTRLS;
    $scope.extdata.themes = THEMES;
    $scope.extdata.categories = CATEGORIES;
}
let PREVIEW_URL = async (app_id) => {
    return APP_URL + "preview/" + app_id;
}