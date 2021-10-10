var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);
    $scope.event = {};
    $scope.orgappid = app_id;

    var tabs = ['kwargs', 'api', 'html', 'js', 'css'];

    $scope.status = { tab: {} };
    $scope.editors = { tab: {} };
    $scope.monaco_properties = { tab: {} };

    $scope.loaded = false;
    $scope.activetab = null;

    $scope.event.active = function (tab) {
        $scope.activetab = tab;
    }

    $scope.event.treeitem = function (item) {
        $scope.info = item;
        app_id = $scope.info.id;
        if (typeof ($scope.info.properties) == 'string') {
            $scope.info.properties = JSON.parse($scope.info.properties);
        }
        if (!$scope.info.properties) $scope.info.properties = {};
        if (!$scope.info.properties.html) $scope.info.properties.html = 'pug';
        if (!$scope.info.properties.js) $scope.info.properties.js = 'javascript';
        if (!$scope.info.properties.css) $scope.info.properties.css = 'less';

        $scope.event.iframe();
        $timeout();
    }

    function langselect(tab) {
        var obj = $scope.options.tab[tab + '_val'];
        if (obj == 'kwargs') return 'python';
        if (obj == 'api') return 'python';
        if ($scope.info.properties[$scope.options.tab[tab + '_val']]) {
            return $scope.info.properties[$scope.options.tab[tab + '_val']];
        }
        return $scope.options.tab[tab + '_val'];
    }

    $scope.event.change = function (targettab, view) {
        $scope.options.tab[targettab + '_val'] = view;
        if (view == 'preview') { $timeout(); return $scope.event.iframe() }
        if (view == 'iframe') { $timeout(); return };
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
        $scope.options.infotab = 1;
        $scope.options.sidemenu = true;
    }

    if ($scope.options.panel_status) $scope.options.panel_status = {};

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
        var _height = $('#editor-area').height();
        var _width = $('#editor-area').width();

        function _horizonal_split() {
            $scope.properties.horizonal.lastComponentSize = Math.round(_height / 2);
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
        $scope.info.html = $scope.info.html.replace(/\t/gim, '    ');
        $scope.info.css = $scope.info.css.replace(/\t/gim, '    ');
        $scope.info.js = $scope.info.js.replace(/\t/gim, '    ');
        $scope.info.api = $scope.info.api.replace(/\t/gim, '    ');
        $scope.info.kwargs = $scope.info.kwargs.replace(/\t/gim, '    ');

        var data = angular.copy($scope.info);
        data.properties = JSON.stringify(data.properties);

        $.post(API.UPDATE, data, function (res) {
            $scope.event.iframe();
            if (cb) return cb(res);
            if (res.code == 200) {
                return toastr.success('저장되었습니다');
            }
            toastr.error('오류가 발생하였습니다.');
        });
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
            $scope.event.save();
        };
        fr.readAsText($('#import-file').prop('files')[0]);
    });

    $.get(API.TREE, function (res) {
        $scope.tree = res.data;
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
        $scope.monaco_properties.tab.tab4 = $scope.monaco(langselect('tab4'));

        function bindonload(targettab) {
            $scope.monaco_properties.tab[targettab].onLoad = function (editor) {
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.RightArrow, function () {
                    var next = tabs[(tabs.indexOf($scope.options.tab[targettab + "_val"]) + 1) % tabs.length];
                    $scope.event.change(targettab, next);
                });

                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.LeftArrow, function () {
                    var prev = tabs.indexOf($scope.options.tab[targettab + "_val"]) - 1;
                    if (prev < 0) {
                        prev = tabs[tabs.length - 1];
                    } else {
                        prev = tabs[prev];
                    }

                    $scope.event.change(targettab, prev);
                });

                $scope.editors[targettab] = editor;
            }
        }

        for (var i = 1; i <= 4; i++)
            bindonload('tab' + i);

        $timeout(function () {
            $timeout(function () {
                $scope.event.layout($scope.options.layout);
                $scope.loaded = true;
                $timeout(function () {
                    $scope.event.iframe();
                }, 100);
            }, 1000);
        }, 1000);

        // shortcut

        function shortcuts() {
            shortcutjs(window, {
                'Ctrl KeyS': function (ev) {
                    $scope.event.save();
                    ev.preventDefault();
                },
                'Ctrl Digit1': function (ev) {
                    $scope.event.active('tab1')
                    $scope.editors['tab1'].focus();
                    ev.preventDefault();
                },
                'Ctrl Digit2': function (ev) {
                    $scope.event.active('tab2')
                    $scope.editors['tab2'].focus();
                    ev.preventDefault();
                },
                'Ctrl Digit3': function (ev) {
                    $scope.event.active('tab3')
                    $scope.editors['tab3'].focus();
                    ev.preventDefault();
                },
                'Ctrl Digit4': function (ev) {
                    $scope.event.active('tab4')
                    $scope.editors['tab4'].focus();
                    ev.preventDefault();
                }
            });
        }

        shortcuts();
        window.addEventListener("focus", shortcuts, false);
    });
};