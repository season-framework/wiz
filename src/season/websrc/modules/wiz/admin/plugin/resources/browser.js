API_URL = "/wiz/admin/api/file";
LOCALSTORAGEID = "season.wiz.plugin.resources.properties";
TREE_DATA = [
    { path: TARGET_PATH, name: TARGET, type: 'folder', icon: 'fa-layer-group', display: TARGET }
];

VIEWER_IMAGE_URL = (item) => {
    let url = item.url;
    url = url.split("/");
    let plugin_id = url[2];
    url = url.splice(4);
    url = url.join("/");
    url = "/resources/wiz/plugin/" + plugin_id + "/" + url;
    return url;
};