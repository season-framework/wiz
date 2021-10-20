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
    $scope.updating = true;

    // wiz
    $scope.event.active = function (tab) {
        $scope.activetab = tab;
        $timeout();
    }

    $scope.tree_selected = {};

    $scope.event.treeitem = function (item) {
        $scope.tree_selected = item;
        $scope.updating = true;
        app_id = item.id;
        $scope.loading = false;
        $timeout();
        $.get(API_URL + '/wiz/info/' + app_id, function (res) {
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

            $scope.commit.load();

            $timeout(function () {
                $scope.updating = false;
            }, 100);
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

    var API_URL = "/wiz/admin/api";
    var API = {
        INFO: API_URL + '/wiz/info/' + app_id,
        DELETE: API_URL + '/wiz/delete',
        UPDATE: API_URL + '/wiz/update/' + app_id,
        UPLOAD: API_URL + '/wiz/upload',
        TREE: API_URL + '/wiz/tree',
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
                            location.href = "/wiz/admin/editor/" + $scope.tree[i].data[j].id;
                            return;
                        }
                    }
                }
            }

            for (var i = 0; i < $scope.tree.length; i++) {
                for (var j = 0; j < $scope.tree[i].data.length; j++) {
                    if ($scope.tree[i].data[j].id != $scope.orgappid) {
                        location.href = "/wiz/admin/editor/" + $scope.tree[i].data[j].id;
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

            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
                socket.emit("edit", { tab: tab, data: $scope.info[tab], room: app_id });
            }

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
        $scope.treedataobj = [];

        for (var i = 0; i < $scope.tree.length; i++) {
            for (var j = 0; j < $scope.tree[i].data.length; j++) {
                $scope.treedata.push($scope.tree[i].data[j].id);
                var treeobj = $scope.tree[i].data[j];
                $scope.treedataobj.push(treeobj);
                if ($scope.tree[i].data[j].id == app_id) {
                    $scope.tree_selected = treeobj;
                }
            }
        }
        $timeout();
    });

    $.get(API.INFO, function (res) {
        $scope.updating = true;
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
                $scope.updating = false;
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
                        if (pre == 'commit') {
                            $scope.event.layout($scope.options.layout);
                        }
                    });
                    ev.preventDefault();
                },
                'Alt Digit2': function (ev) {
                    var pre = $scope.options.panel;
                    $scope.options.panel = 'tree';
                    $timeout(function () {
                        if (pre == 'commit') {
                            $scope.event.layout($scope.options.layout);
                        }
                    });
                    ev.preventDefault();
                },
                'Alt Digit3': function (ev) {
                    $scope.options.panel = 'commit';
                    $timeout();
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

        // commit control
        $scope.commit = {};
        $scope.commit.data = {};
        $scope.commit.diff = {};
        $scope.commit.diff.main = {};
        $scope.commit.diff.compare = {};
        $scope.commit.target = {};

        $scope.commit.monaco = { enableSplitViewResizing: false, fontSize: 14 };
        $scope.commit.view = "kwargs";

        $scope.commit.revert = function () {
            if ($scope.commit.target.diff) {
                $scope.info = angular.copy($scope.commit.target.diff);
                $scope.info.version = "master";
                $scope.info.version_name = "master";
                $scope.info.version_message = "";
                $scope.commit.target.selected = $scope.info;
                $scope.commit.change();                        
            }
                
            $timeout();
        }

        $scope.commit.change = function (view) {
            if (view) $scope.commit.view = view;
            else view = $scope.commit.view;

            if (!$scope.commit.target.selected) {
                $timeout();
                return;
            }
            if (!$scope.commit.target.diff) {
                $scope.commit.target.diff = { properties: {} };
            }

            var lang1 = "python";
            try {
                lang1 = $scope.commit.target.selected.properties[view]
            } catch (e) {
            }
            if (!lang1) lang1 = "python";

            var lang2 = "python";
            try {
                lang2 = $scope.commit.target.diff.properties[view]
            } catch (e) {
            }
            if (!lang2) lang2 = "python";

            $scope.commit.diff = {
                main: {
                    code: $scope.commit.target.selected[view],
                    language: lang1
                },
                compare: {
                    code: $scope.commit.target.diff[view],
                    language: lang2
                }
            }

            $timeout();
        }

        $scope.commit.load = function () {
            $.post("/wiz/admin/api/wiz/commit_log", { id: app_id }, function (res) {
                $scope.commit.logs = res.data;
                $scope.commit.target = {};
                $scope.commit.event.item($scope.commit.logs[0]);
                $timeout();
            });
        }

        $scope.commit.event = {};

        $scope.commit.event.item = function (item) {
            $.post("/wiz/admin/api/wiz/commit_get", item, function (res) {
                $scope.commit.target.selected = res.data;
                $scope.commit.change();
            });
        }

        $scope.commit.event.diff = function (item) {
            if ($scope.commit.target.diff.version == item.version) {
                $scope.commit.target.diff = null;
                $scope.commit.change();
                return;
            }
            $.post("/wiz/admin/api/wiz/commit_get", item, function (res) {
                $scope.commit.target.diff = res.data;
                $scope.commit.change();
            });
        }

        $scope.commit.event.save = function (data) {
            var pd = angular.copy($scope.info);
            pd.version_name = data.version_name;
            pd.version_message = data.version_message;
            $.post("/wiz/admin/api/wiz/commit", pd, function (res) {
                $scope.commit.data = {};
                $scope.commit.load();
            });
        };

        $scope.commit.load();
    });

    $scope.debuglog = "";

    $scope.event.clear_debug = function () {
        $scope.debuglog = "";
        $timeout();
    }

    // socketio
    var ansi_up = new AnsiUp();
    var socket = io("/wiz");

    socket.on("connect", function (data) {
        if (!data) return;
        $scope.session.id = data.sid;
        socket.emit("join", { id: app_id });
    });

    $scope.session = {};
    $scope.session.cache = {};

    var doupdate = function () {
        var keys = Object.keys($scope.session.cache);
        if (keys.length == 0) {
            setTimeout(doupdate, 200);
            return;
        }

        $scope.updating = true;

        for (var i = 0; i < keys.length; i++) {
            var key = keys[i]
            var code = $scope.session.cache[key];
            $scope.info[key] = code;
            delete $scope.session.cache[key];
        }

        $timeout(function () {
            $timeout(function () {
                $scope.updating = false;
                doupdate();
            });
        });
    }

    doupdate();

    socket.time = 0;
    socket.limit = 2000;

    for (var i = 0; i < tabs.length; i++) {
        function watcher(tab) {
            $scope.$watch("info." + tab, function () {
                if (!$scope.info) return;
                if ($scope.updating) return;
                var isstart = new Date().getTime() - socket.time;
                if (isstart > socket.limit) {
                    socket.emit("edit", { tab: tab, data: $scope.info[tab], room: app_id });
                    socket.time = new Date().getTime();
                    return;
                }

                socket.time = new Date().getTime();
                $timeout(function () {
                    var now = new Date().getTime();
                    var diff = now - socket.time;
                    if (diff > socket.limit) {
                        socket.emit("edit", { tab: tab, data: $scope.info[tab], room: app_id });
                    }
                }, socket.limit);
            });
        }
        var tab = tabs[i];
        watcher(tab);
    }

    $scope.$watch("info.id", function (next, prev) {
        if (!prev) return;
        if (!$scope.info) return;
        socket.emit("leave", { id: prev });
        socket.emit("join", { id: next });
    });

    $scope.$watch("info.title", function (next, prev) {
        if (!$scope.tree_selected) return;
        $scope.tree_selected.title = next;
        $timeout();
    });

    $scope.$watch("info.namespace", function (next, prev) {
        if (!$scope.tree_selected) return;
        $scope.tree_selected.namespace = next;
        $timeout();
    });

    socket.on("message", function (data) {
        if (data.type == "status") {
            $scope.session.users = data.users;
            $timeout();
        } else if (data.type == "edit") {
            if (data.room != app_id) return;
            if (data.sid == $scope.session.id) return;
            var tab = data.tab;
            var code = data.data;
            $scope.session.cache[tab] = code;
        }
    });

    socket.on("log", function (data) {
        data = data.replace(/ /gim, "__SEASONWIZPADDING__");
        data = ansi_up.ansi_to_html(data).replace(/\n/gim, '<br>').replace(/__SEASONWIZPADDING__/gim, '<div style="width: 6px; display: inline-block;"></div>');
        $scope.debuglog = $scope.debuglog + data;
        $timeout(function () {
            var element = $('.debug-messages')[0];
            if (!element) return;
            element.scrollTop = element.scrollHeight - element.clientHeight;
        });
    });
};