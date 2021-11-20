API_URL = "/wiz/admin/api/file";
LOCALSTORAGEID = "season.wiz.resources.properties";
TREE_DATA = [
    { path: BRANCHPATH, name: "config", type: 'folder', icon: 'fa-layer-group', display: "Config" },
    { path: BRANCHPATH, name: "compiler", type: 'folder', icon: 'fa-rocket', display: "Compiler" }
];

VIEWER_IMAGE_URL = (item) => { 
    return false;
};