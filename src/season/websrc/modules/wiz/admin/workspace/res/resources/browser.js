API_URL = "/wiz/admin/api/file";
LOCALSTORAGEID = "season.wiz.resources.properties";
TREE_DATA = [
    { path: BRANCHPATH, name: "resources", type: 'folder', icon: 'fa-layer-group', display: "Resources" }
];

VIEWER_IMAGE_URL = (item) => { 
    let url = item.url;
    url = url.split("/");
    url = url.splice(3);
    url = url.join("/");
    return "/" + url;
};