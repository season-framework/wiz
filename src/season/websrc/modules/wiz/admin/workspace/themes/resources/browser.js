API_URL = "/wiz/admin/workspace/themes/api";
LOCALSTORAGEID = "season.wiz.resources.properties";
TREE_DATA = [];
for (let i = 0; i < THEMES.length; i++) {
    let theme = THEMES[i];
    let obj = {
        path: BRANCHPATH + "/themes", name: theme, type: 'folder', icon: 'fa-layer-group',
        onFolder: async (item) => {
            item.checked = false;
            for (var i = 0; i < item.sub.length; i++) {
                item.sub[i].hide_menu = true;
                if (item.sub[i].type == 'file') item.sub[i].icon = 'fa-file'
                else if (item.sub[i].type == 'folder') item.sub[i].icon = 'fa-folder'
                else if (item.sub[i].type == 'layout') item.sub[i].icon = 'fa-columns'
                else item.sub[i].icon = 'fa-caret-right'
            }
            return item;
        }
    };
    TREE_DATA.push(obj)
}

TREE_DATA.push({
    path: '', name: "New Theme", icon: 'fa-plus-square', click: async ($scope, item) => {
        $scope.modal.data.newtheme = {};
        $scope.modal.data.newtheme.title = "";
        $scope.modal.data.newtheme.create = async (title) => {
            let data = { path: BRANCHPATH + "/themes", name: title, rename: title };
            await $scope.API.rename(data);
            $('#modal-new-theme').modal('hide');
            location.reload();
        };
        $('#modal-new-theme').modal('show');
    }
});

VIEWER_IMAGE_URL = (item) => {
    let url = item.url;
    url = url.split("/");
    let themename = url[2];
    url = url.splice(4);
    url = url.join("/");
    url = "/resources/themes/" + themename + "/" + url;
    return url;
};

BUILD_INIT = async ($scope) => {
    console.log($scope);
}