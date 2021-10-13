var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);
    $scope.trustAsHtml = $sce.trustAsHtml;
    $scope.event = {};
    $scope.orgappid = app_id;

    var tabs = ['kwargs', 'api', 'socketio', 'html', 'js', 'css'];

    $scope.status = {};
    $scope.editors = {};
    $scope.monaco_properties = { tab: {} };

    $scope.loaded = false;
    $scope.loading = true;
    $scope.activetab = 'tab1';

    // wiz
    $scope.event.active = function (tab) {
        $scope.activetab = tab;
        $timeout();
    }

    $scope.event.treeitem = function (item) {
        app_id = item.id;
        $scope.loading = false;
        $timeout();
        $.get(API_URL + '/api/info/' + app_id, function (res) {
            if (res.data.id != app_id) return;
            $scope.info = res.data;
            if (typeof ($scope.info.properties) == 'string') {
                $scope.info.properties = JSON.parse($scope.info.properties);
            }
            if (!$scope.info.properties) $scope.info.properties = {};
            if (!$scope.info.properties.html) $scope.info.properties.html = 'pug';
            if (!$scope.info.properties.js) $scope.info.properties.js = 'javascript';
            if (!$scope.info.properties.css) $scope.info.properties.css = 'less';

            $scope.event.iframe();
            $scope.loading = true;
            $scope.editors[$scope.activetab].focus();
            $timeout();
        });
    }

    function langselect(tab) {
        var obj = $scope.options.tab[tab + '_val'];
        if (obj == 'kwargs') return 'python';
        if (obj == 'api') return 'python';
        if (obj == 'socketio') return 'python';
        if ($scope.info.properties[$scope.options.tab[tab + '_val']]) {
            return $scope.info.properties[$scope.options.tab[tab + '_val']];
        }
        return $scope.options.tab[tab + '_val'];
    }

    $scope.event.change = function (targettab, view) {
        var previous_view = $scope.options.tab[targettab + '_val'];
        if ($scope.editors[targettab]) {
            $scope.status[targettab + '-' + previous_view] = [$scope.editors[targettab].getModel(), $scope.editors[targettab].saveViewState()];
        }

        $scope.options.tab[targettab + '_val'] = view;
        if (view == 'preview') { $timeout(); return $scope.event.iframe() }
        if (view == 'iframe') { $timeout(); return };
        if (view == 'debug') { $timeout(); return };

        var language = $scope.monaco_properties.tab[targettab].language = langselect(targettab);
        if ($scope.editors[targettab]) {
            var model = $scope.editors[targettab].getModel();
            monaco.editor.setModelLanguage(model, language);
        }
        $timeout();
    }

    // editor options
    try {
        $scope.options = JSON.parse(localStorage["season.wiz.option"])
    } catch (e) {
        $scope.options = {};
        $scope.options.panel = "component";
        $scope.options.layout = 2;
        $scope.options.tab = {};
        $scope.options.tab['tab1_val'] = 'kwargs';
        $scope.options.tab['tab2_val'] = 'html';
        $scope.options.tab['tab3_val'] = 'preview';
        $scope.options.tab['tab4_val'] = 'debug';
        $scope.options.infotab = 1;
        $scope.options.sidemenu = true;
    }

    if (!$scope.options.panel) $scope.options.panel = 'component';
    if (!$scope.options.panel_status) $scope.options.panel_status = {};

    $scope.codetypes = {};
    $scope.codetypes.html = ['pug', 'html'];
    $scope.codetypes.js = ['javascript', 'typescript'];
    $scope.codetypes.css = ['less', 'css', 'scss'];

    $scope.$watch("options", function () {
        var opt = angular.copy($scope.options);
        localStorage["season.wiz.option"] = JSON.stringify(opt);
    }, true);

    // split pane properties
    try {
        var properties = JSON.parse(localStorage["season.wiz.properties"]);
        delete properties.root.lastComponentSize;
        $scope.properties = properties;
    } catch (e) {
        $scope.properties = {};
        $scope.properties.root = {};
        $scope.properties.horizonal = {};
        $scope.properties.vertical_1_1 = {};
        $scope.properties.vertical_1_2 = {};
    }

    $scope.$watch("properties", function () {
        var opt = angular.copy($scope.properties);
        localStorage["season.wiz.properties"] = JSON.stringify(opt);
    }, true);

    $scope.event.layout = function (layout) {
        $scope.options.layout = layout;

        if (layout == 1) {
            $scope.accessable_tab = ['tab1'];
        } else if (layout == 2) {
            $scope.accessable_tab = ['tab1', 'tab2'];
        } else if (layout == 3) {
            $scope.accessable_tab = ['tab1', 'tab2', 'tab3'];
        } else if (layout == 4) {
            $scope.accessable_tab = ['tab1'];
        } else if (layout == 5) {
            $scope.accessable_tab = ['tab1', 'tab2'];
        } else if (layout == 6) {
            $scope.accessable_tab = ['tab1', 'tab2', 'tab3'];
        }

        var _height = $('#editor-area').height();
        var _width = $('#editor-area').width();

        function _horizonal_split() {
            var h = Math.round(_height / 3);
            if (h > 400) h = 400;
            $scope.properties.horizonal.lastComponentSize = h;
        }

        function _horizonal_top() {
            $scope.properties.horizonal.lastComponentSize = 0;
        }

        if (layout == 1) {
            _horizonal_top();
            $scope.properties.vertical_1_1.lastComponentSize = 0;
        } else if (layout == 2) {
            _horizonal_top();
            $scope.properties.vertical_1_1.lastComponentSize = Math.round(_width / 2);
            $scope.properties.vertical_1_2.lastComponentSize = 0;
        } else if (layout == 3) {
            _horizonal_top();
            $scope.properties.vertical_1_1.lastComponentSize = Math.round(_width / 3 * 2);
            $scope.properties.vertical_1_2.lastComponentSize = Math.round(_width / 3);
        } else if (layout == 4) {
            _horizonal_split();
            $scope.properties.vertical_1_1.firstComponentSize = _width;
            $scope.properties.vertical_1_1.lastComponentSize = 0;
        } else if (layout == 5) {
            _horizonal_split();
            $scope.properties.vertical_1_1.firstComponentSize = Math.round(_width / 2);
            $scope.properties.vertical_1_1.lastComponentSize = Math.round(_width / 2);
            $scope.properties.vertical_1_2.firstComponentSize = Math.round(_width / 2);
            $scope.properties.vertical_1_2.lastComponentSize = 0;
        } else if (layout == 6) {
            _horizonal_split();
            $scope.properties.vertical_1_1.firstComponentSize = Math.round(_width / 3);
            $scope.properties.vertical_1_1.lastComponentSize = Math.round(_width / 3 * 2);
            $scope.properties.vertical_1_2.firstComponentSize = Math.round(_width / 3);
            $scope.properties.vertical_1_2.lastComponentSize = Math.round(_width / 3);
        }

        $timeout();
    }

    $scope.trustAsHtml = $sce.trustAsHtml;
    $scope.math = Math;

    $scope.category = category;
    $scope.theme = [];
    for (var key in theme) {
        $scope.theme.push(key);
    }

    $scope.tinymce_opt = $scope.tinymce({});
    $scope.tinymce_opt.onLoad = function (editor) {
        editor.addShortcut('meta+S', 'Save', function () {
            setTimeout(function () {
                $scope.event.save();
            }, 300);
        });
    }

    var API_URL = "/wiz/widget";
    var API = {
        INFO: API_URL + '/api/info/' + app_id,
        DELETE: API_URL + '/api/delete',
        UPDATE: API_URL + '/api/update/' + app_id,
        UPLOAD: API_URL + '/api/upload',
        TREE: API_URL + '/api/tree',
        LIST: API_URL,
        IFRAME: function (app_id) {
            if ($scope.info) {
                if ($scope.info.viewuri) {
                    return $scope.info.viewuri;
                }
            }

            return "/wiz/iframe/" + app_id + '?time=' + new Date().getTime();
        }
    };

    $scope.event.delete = function () {
        $.get(API.DELETE, { app_id: app_id }, function (res) {
            for (var i = 0; i < $scope.tree.length; i++) {
                if ($scope.tree[i].id == $scope.info.category) {
                    for (var j = 0; j < $scope.tree[i].data.length; j++) {
                        if ($scope.tree[i].data[j].id != $scope.orgappid) {
                            location.href = "/wiz/widget/editor/" + $scope.tree[i].data[j].id;
                            return;
                        }
                    }
                }
            }

            for (var i = 0; i < $scope.tree.length; i++) {
                for (var j = 0; j < $scope.tree[i].data.length; j++) {
                    if ($scope.tree[i].data[j].id != $scope.orgappid) {
                        location.href = "/wiz/widget/editor/" + $scope.tree[i].data[j].id;
                        return;
                    }
                }
            }

            location.href = API.LIST + "/list/" + $scope.info.category;
        });
    }

    $scope.event.modal = {};
    $scope.event.modal.delete = function () {
        $('#modal-delete').modal('show');
    }

    $scope.event.iframe = function (findurl) {
        var url = API.IFRAME(app_id);
        if (findurl) {
            return url;
        }

        $scope.iframe_load = true;
        $timeout(function () {
            $('iframe.preview').attr('src', url);
            $('iframe.preview').on('load', function () {
                $scope.iframe_load = false;
                $timeout();
            });
        });
    };

    $scope.event.save = function (cb) {
        if ($scope.options.panel == 'sf') {
            $scope.framework.save();
            return;
        }

        if ($scope.info.html) $scope.info.html = $scope.info.html.replace(/\t/gim, '    ');
        if ($scope.info.css) $scope.info.css = $scope.info.css.replace(/\t/gim, '    ');
        if ($scope.info.js) $scope.info.js = $scope.info.js.replace(/\t/gim, '    ');
        if ($scope.info.api) $scope.info.api = $scope.info.api.replace(/\t/gim, '    ');
        if ($scope.info.kwargs) $scope.info.kwargs = $scope.info.kwargs.replace(/\t/gim, '    ');
        if ($scope.info.socketio) $scope.info.socketio = $scope.info.socketio.replace(/\t/gim, '    ');

        var data = angular.copy($scope.info);
        data.properties = JSON.stringify(data.properties);

        $.post(API.UPDATE, data, function (res) {
            $scope.event.iframe();
            if (cb) return cb(res);
            if (res.code == 200) {
                return toastr.success('Saved');
            }
            toastr.error(res.error ? res.error : 'Error');
        });
    }

    $scope.event.keymaps = function () {
        $('#modal-keymaps').modal('show');
    }

    $scope.event.search = function (val) {
        for (var i = 0; i < $scope.tree.length; i++) {
            try {
                for (var j = 0; j < $scope.tree[i].data.length; j++) {
                    var ns = $scope.tree[i].data[j].namespace;
                    var title = $scope.tree[i].data[j].title;
                    $scope.tree[i].data[j].hide = true;
                    if (ns.includes(val) || title.includes(val)) {
                        $scope.tree[i].data[j].hide = false;
                    }

                    if (val.length == 0) {
                        $scope.tree[i].data[j].hide = false;
                    }
                }
            } catch (e) {
            }
        }
    }

    // import from file
    $scope.event.select_file = function () {
        $('#import-file').click();
    }

    $('#import-file').change(function () {
        var fr = new FileReader();
        fr.onload = function () {
            var data = fr.result;
            var json = JSON.parse(data);
            $scope.info.html = json.html;
            $scope.info.js = json.js;
            $scope.info.css = json.css;
            $scope.info.api = json.api;
            $scope.info.kwargs = json.kwargs;
            $scope.info.socketio = json.socketio;
            $scope.event.save();
        };
        fr.readAsText($('#import-file').prop('files')[0]);
    });

    $.get(API.TREE, function (res) {
        $scope.tree = res.data;
        $scope.treedata = [];
        $scope.treedataobj = []
        for (var i = 0; i < $scope.tree.length; i++) {
            for (var j = 0; j < $scope.tree[i].data.length; j++) {
                $scope.treedata.push($scope.tree[i].data[j].id);
                $scope.treedataobj.push($scope.tree[i].data[j]);
            }
        }
        $timeout();
    });

    $.get(API.INFO, function (res) {
        $scope.info = res.data;
        if (!$scope.info.theme) $scope.info.theme = "default";

        if (!$scope.info.properties) $scope.info.properties = {};
        if (!$scope.info.properties.html) $scope.info.properties.html = 'pug';
        if (!$scope.info.properties.js) $scope.info.properties.js = 'javascript';
        if (!$scope.info.properties.css) $scope.info.properties.css = 'less';

        // monaco options
        $scope.$watch('info.properties.html', function () {
            for (var targettab in $scope.monaco_properties.tab) {
                if ($scope.options.tab[targettab + "_val"] == "html") {
                    $scope.event.change(targettab, "html");
                }
            }
        });

        $scope.$watch('info.properties.css', function () {
            for (var targettab in $scope.monaco_properties.tab) {
                if ($scope.options.tab[targettab + "_val"] == "css") {
                    $scope.event.change(targettab, "css");
                }
            }
        });

        $scope.$watch('info.properties.js', function () {
            for (var targettab in $scope.monaco_properties.tab) {
                if ($scope.options.tab[targettab + "_val"] == "js") {
                    $scope.event.change(targettab, "js");
                }
            }
        });

        $scope.monaco_properties.tab.tab1 = $scope.monaco(langselect('tab1'));
        $scope.monaco_properties.tab.tab2 = $scope.monaco(langselect('tab2'));
        $scope.monaco_properties.tab.tab3 = $scope.monaco(langselect('tab3'));

        function bindonload(targettab) {
            $scope.monaco_properties.tab[targettab].onLoad = function (editor) {
                editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KEY_A, function () {
                    var prev = tabs.indexOf($scope.options.tab[targettab + "_val"]) - 1;
                    if (prev < 0) {
                        prev = tabs[tabs.length - 1];
                    } else {
                        prev = tabs[prev];
                    }

                    $scope.event.change(targettab, prev);
                    shortcuts();
                });

                editor.addCommand(monaco.KeyMod.Alt | monaco.KeyCode.KEY_S, function () {
                    var next = tabs[(tabs.indexOf($scope.options.tab[targettab + "_val"]) + 1) % tabs.length];
                    $scope.event.change(targettab, next);
                    shortcuts();
                });

                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, function () {
                    $scope.event.save();
                    shortcuts();
                });

                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_K, function () {
                    $scope.event.clear_debug();
                    shortcuts();
                });

                $scope.editors[targettab] = editor;
            }
        }

        for (var i = 1; i <= 3; i++)
            bindonload('tab' + i);

        $timeout(function () {
            $scope.loaded = true;
            $timeout(function () {
                $scope.event.layout($scope.options.layout);
                $scope.event.iframe();
            }, 1000);
        }, 1000);

        // shortcut
        function shortcuts() {
            $(window).unbind();
            shortcutjs(window, {
                'Alt Digit1': function (ev) {
                    var pre = $scope.options.panel;
                    $scope.options.panel = 'component';
                    $timeout(function () {
                        if (pre == 'sf') {
                            $scope.event.layout($scope.options.layout);
                        }
                    });
                    ev.preventDefault();
                },
                'Alt Digit2': function (ev) {
                    var pre = $scope.options.panel;
                    $scope.options.panel = 'tree';
                    $timeout(function () {
                        if (pre == 'sf') {
                            $scope.event.layout($scope.options.layout);
                        }
                    });
                    ev.preventDefault();
                },
                'Alt Digit3': function (ev) {
                    $scope.options.panel = 'sf';
                    $timeout(function () {
                        if ($scope.framework.editor)
                            $scope.framework.editor.focus();
                    });
                    ev.preventDefault();
                },
                'Alt KeyJ': function (ev) {
                    ev.preventDefault();
                    $(window).focus();
                    var appidx = $scope.treedata.indexOf(app_id) - 1;
                    if (appidx < 0) appidx = $scope.treedata.length - 1
                    var cnt = 0;
                    while ($scope.treedataobj[appidx].hide) {
                        appidx = appidx - 1;
                        cnt++;
                        if (cnt > $scope.treedata.length) return;
                    }
                    appidx = $scope.treedata[appidx];
                    $scope.event.treeitem({ id: appidx });
                },
                'Alt KeyK': function (ev) {
                    ev.preventDefault();
                    $(window).focus();
                    var appidx = ($scope.treedata.indexOf(app_id) + 1) % $scope.treedata.length;
                    var cnt = 0;
                    while ($scope.treedataobj[appidx].hide) {
                        appidx = (appidx + 1) % $scope.treedata.length;
                        cnt++;
                        if (cnt > $scope.treedata.length) return;
                    }
                    appidx = $scope.treedata[appidx];
                    $scope.event.treeitem({ id: appidx });
                },
                'Ctrl KeyS': function (ev) {
                    $scope.event.save();
                    ev.preventDefault();
                },
                'Ctrl KeyK': function (ev) {
                    $scope.event.clear_debug();
                    ev.preventDefault();
                },
                'Alt KeyF': function (ev) {
                    $('#search').focus();
                    ev.preventDefault();
                },
                'Alt KeyZ': function (ev) {
                    ev.preventDefault();
                    if (!$scope.accessable_tab) return;
                    var tab = 'tab1';
                    if (!$scope.activetab) tab = 'tab1';
                    else tab = $scope.activetab;
                    tab = $scope.accessable_tab.indexOf(tab) - 1;
                    if (tab < 0) tab = $scope.accessable_tab.length - 1;
                    tab = $scope.accessable_tab[tab];

                    var obj = $scope.options.tab[tab + '_val'];
                    if (obj == 'preview') {
                        tab = $scope.accessable_tab.indexOf(tab) - 1;
                        if (tab < 0) tab = $scope.accessable_tab.length - 1;
                        tab = $scope.accessable_tab[tab];
                    }

                    $scope.event.active(tab);
                    $scope.editors[tab].focus();
                },
                'Alt KeyX': function (ev) {
                    ev.preventDefault();
                    if (!$scope.accessable_tab) return;
                    var tab = 'tab1';
                    if (!$scope.activetab) tab = 'tab1';
                    else tab = $scope.activetab;
                    tab = $scope.accessable_tab.indexOf(tab) + 1;
                    if (tab > $scope.accessable_tab.length - 1) tab = 0;
                    tab = $scope.accessable_tab[tab];

                    var obj = $scope.options.tab[tab + '_val'];
                    if (obj == 'preview') {
                        tab = $scope.accessable_tab.indexOf(tab) + 1;
                        if (tab > $scope.accessable_tab.length - 1) tab = 0;
                        tab = $scope.accessable_tab[tab];
                    }

                    $scope.event.active(tab);
                    $scope.editors[tab].focus();
                }
            });
        }

        shortcuts();
        window.addEventListener("focus", shortcuts, false);

        // framework editor
        $scope.framework = {};
        $scope.framework.editorshow = false;
        $scope.monaco_properties.framework = $scope.monaco("python");

        $scope.framework.tree = [];
        $scope.framework.tree.push({ path: 'app', name: 'config', sub: [], type: 'folder', root: true });
        $scope.framework.tree.push({ path: 'app', name: 'filter', sub: [], type: 'folder', root: true });
        $scope.framework.tree.push({ path: 'app', name: 'interfaces', sub: [], type: 'folder', root: true });
        $scope.framework.tree.push({ path: 'app', name: 'model', sub: [], type: 'folder', root: true });
        if (thememodule)
            $scope.framework.tree.push({ path: 'modules', name: thememodule, sub: [], type: 'folder', root: true });
        $scope.framework.parents = {};

        $scope.framework.save = function () {
            var data = angular.copy($scope.framework.item);
            $.post('/wiz/widget/sf/update', data, function (res) {
                if (res.code == 200) {
                    return toastr.success('Saved');
                }

                return toastr.error('Error');
            });
        }

        $scope.framework.delete = function () {
            var data = angular.copy($scope.framework.selected_delete);
            var parent = $scope.framework.parents[data.path + "/" + data.name];
            $.post('/wiz/widget/sf/delete', data, function (res) {
                $scope.framework.selected_delete = null;
                $scope.framework.loader(parent, function (resp) { });
                $timeout();
            });
            $('#modal-delete-file').modal('hide');
        }

        $scope.framework.modal_delete = function (item) {
            $scope.framework.selected_delete = item;
            $('#modal-delete-file').modal('show');
        }

        $scope.framework.create = function (item, ftype) {
            if (item.type != 'folder') {
                return;
            }

            $scope.framework.loader(item, function () {
                var obj = {};
                obj.path = item.path + "/" + item.name;
                obj.type = ftype;
                obj.name = "";
                item.sub.push(obj);
                $scope.framework.parent = item;
                $timeout(function () {
                    $scope.framework.change_name(item.sub[item.sub.length - 1]);
                });
            });
        }

        $scope.framework.save_name = function () {
            var data = angular.copy($scope.framework.selected);
            $.post('/wiz/widget/sf/rename', data, function (res) {
                if (res.code != 200) {
                    toastr.error(res.data);
                    return;
                }
                $scope.framework.selected.edit = false;
                $scope.framework.selected.name = $scope.framework.selected.rename;

                if ($scope.framework.parent) {
                    $scope.framework.loader($scope.framework.parent, function (resp) { });
                    $scope.framework.parent = null;
                    $timeout();
                } else {
                    $scope.framework.loader($scope.framework.selected, function (resp) { });
                }

                $timeout();
            });
        }

        $scope.framework.change_name = function (item) {
            if ($scope.framework.selected) {
                $scope.framework.selected.edit = false;
            }

            item.edit = true;
            item.rename = item.name + "";
            $scope.framework.selected = item;
            $timeout();
        }

        $scope.framework.loader = function (item, cb) {
            if (!cb) {
                if (item.sub.length > 0) {
                    item.sub = [];
                    $timeout();
                    return;
                }
                cb = function () { };
            }

            $.post('/wiz/widget/sf/tree', { path: item.path, name: item.name, type: item.type }, function (res) {
                if (res.code == 201) {
                    $scope.monaco_properties.framework.language = res.data.language;
                    $scope.framework.editorshow = false;
                    $timeout(function () {
                        $scope.framework.item = res.data;
                        $timeout(function () {
                            $scope.framework.editorshow = true;
                            $timeout();
                        });
                    });
                    return cb(res);
                }

                if (res.code != 200) return cb(res);

                res.data.sort(function (a, b) {
                    if (a.type == 'folder' && b.type != 'folder') return -1;
                    if (a.type != 'folder' && b.type == 'folder') return 1;
                    return a.name.localeCompare(b.name);
                });
                item.sub = res.data;

                for (var i = 0; i < item.sub.length; i++) {
                    $scope.framework.parents[item.sub[i].path + "/" + item.sub[i].name] = item;
                }

                $timeout();
                cb(res);
            });
        }
    });

    $scope.debuglog = "";

    $scope.event.clear_debug = function () {
        $scope.debuglog = "";
        $timeout();
    }

    var ansi_up = new AnsiUp();
    var socket = io("/wiz");
    socket.on("connect", function (data) {
    });
    socket.on("disconnect", function (data) {
    });

    socket.on("log", function (data) {
        data = ansi_up.ansi_to_html(data).replace(/\n/gim, '<br>');
        $scope.debuglog = $scope.debuglog + data;
        $timeout(function () {
            var element = $('.debug-messages')[0];
            if (!element) return;
            element.scrollTop = element.scrollHeight - element.clientHeight;
        });
    });
};