var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);
    $scope.math = Math;
    $scope.trustAsHtml = $sce.trustAsHtml;
    $scope.event = {};
    $scope.status = {};
    $scope.data = {};
    $scope.loaded = true;
    $scope.BASEPATH = BASEPATH;

    $scope.filepathgen = function (data) {
        try {
            var path = data.item.path.substring(BASEPATH.length);
            var filename = data.item.name;
            var themename = path.split("/")[1];
            var target = path.split("/")[2];
            if (target == "resources") {
                path = path.substring(themename.length + target.length + 2);
                var fullpath = "/resources/themes/" + themename + path + "/" + filename;
                if (!path) {
                    fullpath = "/resources/themes/" + themename + "/" + filename;
                }
                return fullpath;
            }
            return path + "/" + filename;
        } catch (e) {
        }
        return "";
    }

    // split pane properties
    try {
        var properties = JSON.parse(localStorage["season.wiz.resources.properties"]);
        delete properties.root.lastComponentSize;
        $scope.properties = properties;
    } catch (e) {
        $scope.properties = {};
        $scope.properties.root = {};
    }

    $scope.$watch("properties", function () {
        var opt = angular.copy($scope.properties);
        localStorage["season.wiz.resources.properties"] = JSON.stringify(opt);
    }, true);

    // shortcut
    function shortcuts() {
        $(window).unbind();
        shortcutjs(window, {
            'Ctrl KeyS': function (ev) {
                $scope.event.save();
                ev.preventDefault();
            }
        });
    }

    shortcuts();
    window.addEventListener("focus", shortcuts, false);

    $scope.status.editor = false;
    $scope.monaco_properties = $scope.monaco("python");
    $scope.monaco_properties.onLoad = function (editor) {
        editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, function () {
            $scope.event.save();
            shortcuts();
        });
    }

    $scope.data.parents = {};
    $scope.data.tree = [];
    for (var i = 0; i < target.length; i++)
        $scope.data.tree.push({ path: target[i].path, name: target[i].name, display: target[i].display, sub: [], type: 'folder', root: true });

    $scope.event.save = function () {
        var data = angular.copy($scope.data.item);
        $.post('/wiz/admin/themes/api/update', data, function (res) {
            if (res.code == 200) {
                return toastr.success('Saved');
            }

            return toastr.error('Error');
        });
    }

    $scope.event.delete = function () {
        var data = angular.copy($scope.data.selected_delete);
        var isreload = data.reload;
        var parent = $scope.data.parents[data.path + "/" + data.name];
        if (data.bulk) {
            parent = data;
            var sub = [];
            for (var i = 0; i < data.sub.length; i++) {
                if (data.sub[i].checked) {
                    sub.push(data.sub[i]);
                }
            }

            $.post('/wiz/admin/themes/api/delete_bulk', { data: JSON.stringify(sub) }, function (res) {
                $scope.data.selected_delete = null;
                $scope.event.loader(parent, null, true);
                $timeout();
            });
        } else {
            $.post('/wiz/admin/themes/api/delete', data, function (res) {
                if (isreload) {
                    location.reload();
                    return;
                }
                $scope.data.selected_delete = null;
                $scope.event.loader(parent, null, true);
                $timeout();
            });
        }

        $('#modal-delete-file').modal('hide');
    }

    $scope.event.modal_delete = function (item, bulk, reload) {
        $scope.data.selected_delete = item;
        if (bulk) $scope.data.selected_delete.bulk = true;
        if (reload) $scope.data.selected_delete.reload = true;
        $('#modal-delete-file').modal('show');
    }

    $scope.event.create_theme_modal = function () {
        $scope.data.theme = {};
        $timeout();
        $('#modal-new-theme').modal('show');
    }

    $scope.event.create_theme = function (title) {
        $.post('/wiz/admin/themes/api/rename', { path: BASEPATH, name: title, rename: title }, function (res) {
            $('#modal-new-theme').modal('hide');
            if (res.code == 402) {
                toastr.error(res.data);
                return;
            }

            if (res.code == 401) {
                toastr.error(res.data);
                return;
            }

            location.reload();
        });
    }

    $scope.event.create = function (item, ftype) {
        if (!['folder', 'layout'].includes(item.type)) {
            return;
        }

        $scope.event.loader(item, function () {
            var obj = {};
            obj.path = item.path + "/" + item.name;
            obj.type = ftype;
            obj.name = "";
            item.sub.push(obj);
            $timeout(function () {
                $scope.event.change_name(item.sub[item.sub.length - 1]);
            });
        });
    }

    $scope.event.save_name = function () {
        var data = angular.copy($scope.data.selected);
        $.post('/wiz/admin/themes/api/rename', data, function (res) {
            if (res.code == 402) {
                toastr.error(res.data);
                return;
            }

            if (res.code == 401) {
                toastr.error(res.data);
                return;
            }

            if (res.code == 200) {
                $scope.data.selected.edit = false;
                $scope.data.selected.name = $scope.data.selected.rename;
            }

            $scope.event.loader($scope.data.item, null, true);
            $timeout();
        });
    }

    $scope.event.change_name = function (item) {
        if ($scope.data.selected) {
            $scope.data.selected.edit = false;
        }

        item.edit = true;
        item.rename = item.name + "";
        $scope.data.selected = item;
        $timeout();
    }

    $scope.event.loader = function (item, cb, refresh, init) {
        if ($scope.data.item && item.name != $scope.data.item.name) {
            refresh = true;
        }

        if (!cb) {
            if (!item.root) {
                if (item.sub.length > 0 && !refresh) {
                    item.sub = [];
                    // var parent = $scope.data.parents[item.path + "/" + item.name];
                    // if (parent) $scope.event.loader(parent, null, true);
                    return;
                }
            }

            cb = function () { };
        }

        $.post('/wiz/admin/themes/api/tree', { path: item.path, name: item.name, type: item.type }, function (res) {
            if (res.code == 201) {
                $scope.monaco_properties.language = res.data.language;
                $scope.status.view = "monaco";
                $scope.status.editor = false;
                $timeout(function () {
                    $scope.data.item = res.data;
                    $timeout(function () {
                        $scope.status.editor = true;
                        $timeout();
                    });
                });
                return cb(res);
            }

            if (res.code == 202) {
                $scope.status.editor = false;
                $scope.status.view = "image";
                $scope.data.item = res.data;
                $timeout();
            }

            if (res.code != 200) return cb(res);

            if (init) {
                if (refresh) {
                    $scope.data.item = item;
                    $scope.data.item.checked = false;
                    $scope.status.view = "folder";
                }
            } else {
                if (item.type == 'layout') {
                    $scope.data.item = item;
                    $scope.data.item.checked = false;
                    $scope.status.view = 'layout'
                    $timeout();
                } else {
                    if (['folder', 'layout'].includes($scope.status.view) || refresh) {
                        $scope.data.item = item;
                        $scope.data.item.checked = false;
                        $scope.status.view = "folder";
                    }
                }
            }

            if (!item.root)
                res.data.sort(function (a, b) {
                    if (a.type == 'folder' && b.type != 'folder') return -1;
                    if (a.type != 'folder' && b.type == 'folder') return 1;
                    return a.name.localeCompare(b.name);
                });
            item.sub = res.data;

            for (var i = 0; i < item.sub.length; i++) {
                $scope.data.parents[item.sub[i].path + "/" + item.sub[i].name] = item;
            }

            $timeout();
            cb(res);
        });
    }

    $scope.event.check_items = function (item) {
        item.checked = !item.checked;
        for (var i = 0; i < item.sub.length; i++) {
            item.sub[i].checked = item.checked;
        }
        $timeout();
    }

    $scope.event.check_item = function (item) {
        item.checked = !item.checked;
        $timeout();
    }

    $scope.event.parent = function () {
        if (!$scope.data.item) return;
        if ($scope.data.item.root) return;

        var parent = $scope.data.parents[$scope.data.item.path + "/" + $scope.data.item.name];
        if (parent) $scope.event.loader(parent, null, true);
    }

    var uploadfile = function (fd) {
        $scope.status.upload = true;
        $scope.status.upload_process = 0;
        $.ajax({
            url: "/wiz/admin/themes/api/upload",
            type: 'POST',
            xhr: function () {
                var myXhr = $.ajaxSettings.xhr();
                if (myXhr.upload) {
                    myXhr.upload.addEventListener('progress', function (event) {
                        var percent = 0;
                        var position = event.loaded || event.position;
                        var total = event.total;
                        if (event.lengthComputable) {
                            percent = Math.round(position / total * 10000) / 100;
                        }
                        $scope.status.upload_process = percent;
                        $timeout();
                    }, false);
                }
                return myXhr;
            },
            data: fd,
            cache: false,
            contentType: false,
            processData: false
        }).always(function (res) {
            $scope.status.upload = false;
            $scope.event.loader($scope.data.item, null, true);
        });
    }

    $scope.status.drop = {};
    $scope.status.drop.text = "Drop File Here!"
    $scope.status.drop.ondrop = function (e, files) {
        var files = files;
        var fd = new FormData();
        var filepath = [];
        fd.append("path", $scope.data.item.path);
        fd.append("name", $scope.data.item.name);
        for (var i = 0; i < files.length; i++) {
            fd.append('file[]', files[i]);
            filepath.push(files[i].filepath);
        }

        fd.append("filepath", JSON.stringify(filepath));
        uploadfile(fd);
    }

    $scope.event.upload = function () {
        $('#file-upload').click();
    };

    var fileinput = document.getElementById('file-upload');
    fileinput.onchange = function () {
        var fd = new FormData($('#file-form')[0]);
        fd.append("path", $scope.data.item.path);
        fd.append("name", $scope.data.item.name);
        uploadfile(fd);
    };

    // Initialize
    for (var i = 0; i < $scope.data.tree.length; i++)
        $scope.event.loader($scope.data.tree[i], null, i === 0, true);
};