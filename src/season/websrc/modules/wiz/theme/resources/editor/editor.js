let content_controller = async ($scope, $timeout, $sce) => {
    _builder($scope, $timeout);

    let hash = location.hash.split("#")[1];
    if (hash) {
        let path = location.pathname.split("/");
        path = path.splice(0, path.length - 1);
        path.push(hash);
        path = path.join("/");
        location.href = path;
    }

    /*
     * define variables
     */
    let BUILDER = {};

    let API = {
        handler: (resolve, reject) => async (res) => {
            if (res.code == 200) resolve(res.data);
            else reject(res);
        },
        search: () => new Promise((resolve) => {
            let url = API_URL + '/search';
            $.get(url, function (res) {
                resolve(res);
            });
        }),
        load: (app_id) => new Promise((resolve) => {
            let url = API_URL + '/info/' + app_id;
            $.get(url, function (res) {
                resolve(res);
            });
        }),
        update: (data) => new Promise((resolve) => {
            let app_id = data.package.id;
            let url = API_URL + '/update/' + app_id;
            $.post(url, { info: JSON.stringify(data) }, function (res) {
                resolve(res);
            });
        }),
        diff: (app_id, commit) => new Promise((resolve, reject) => {
            let url = API_URL + '/diff/' + app_id + '/' + commit;
            $.get(url, function (res) {
                $.get(url, API.handler(resolve, reject));
            });
        }),
        history: () => new Promise((resolve, reject) => {
            let url = API_URL + '/history';
            $.get(url, API.handler(resolve, reject));
        }),
        delete: (app_id) => new Promise((resolve) => {
            let url = API_URL + '/delete/' + app_id;
            $.get(url, function (res) {
                resolve(res);
            });
        }),
        clean: () => new Promise((resolve, reject) => {
            $.get('/wiz/admin/setting/api/config/clean', API.handler(resolve, reject));
        }),
        timeout: (ts) => new Promise((resolve) => {
            $timeout(resolve, ts);
        })
    };

    $scope.API = API;

    /*
     * define variables of scope
     */
    $scope.math = Math;
    $scope.trustAsHtml = $sce.trustAsHtml;
    $scope.configuration = {};       // state data for maintaining ui
    $scope.layout = {};              // controller for layout
    $scope.workspace = {};           // controller for workspace
    $scope.loading = {};             // controller for display loading
    $scope.modal = {};               // controller for modal
    $scope.plugin = {};              // manage plugins for ui components
    $scope.app = {};                 // controller for code editor
    $scope.browse = {};              // controller for code editor
    $scope.shortcut = {};
    $scope.socket = {};
    $scope.history = {};
    $scope.viewer = {};

    /* 
     * load wiz editor options from localstorage
     */
    try {
        let configuration = JSON.parse(localStorage[LOCALSTORAGEID]);
        try { delete configuration.layout.opts.root.lastComponentSize; } catch (e) { }
        $scope.configuration = configuration;
    } catch (e) {
        $scope.configuration = {};
        $scope.configuration.tab = {};
        $scope.configuration.tab['tab1_val'] = TABS[0];
        $scope.configuration.tab['tab2_val'] = TABS[1];
        $scope.configuration.tab['tab3_val'] = TABS[2];
        $scope.configuration.tab['tab4_val'] = 'debug';
        $scope.configuration.layout = 2;
        $scope.configuration.layout_menu_width = 360;
    }

    $scope.$watch("configuration", function () {
        let configuration = angular.copy($scope.configuration);
        localStorage[LOCALSTORAGEID] = JSON.stringify(configuration);
    }, true);

    /* 
     * layout selector using split pane
     */
    BUILDER.layout = async () => {
        $scope.layout.viewstate = {};
        $scope.layout.viewstate.root = { firstComponentSize: $scope.configuration.layout_menu_width };
        $scope.layout.viewstate.horizonal = {};
        $scope.layout.viewstate.vertical_1_1 = {};
        $scope.layout.viewstate.vertical_1_2 = {};

        $scope.layout.active_layout = $scope.configuration.layout;

        $scope.$watch("layout", function () {
            $scope.configuration.layout_menu_width = $scope.layout.viewstate.root.firstComponentSize;
            $scope.configuration.layout = $scope.layout.active_layout;
        }, true);

        $scope.layout.change = async (layout) => {
            $scope.layout.active_layout = layout;

            if (layout == 1) {
                $scope.layout.accessable_tab = ['tab1'];
            } else if (layout == 2) {
                $scope.layout.accessable_tab = ['tab1', 'tab2'];
            } else if (layout == 3) {
                $scope.layout.accessable_tab = ['tab1', 'tab2', 'tab3'];
            } else if (layout == 4) {
                $scope.layout.accessable_tab = ['tab1'];
            } else if (layout == 5) {
                $scope.layout.accessable_tab = ['tab1', 'tab2'];
            } else if (layout == 6) {
                $scope.layout.accessable_tab = ['tab1', 'tab2', 'tab3'];
            }

            let _height = $('#editor-area').height();
            let _width = $('#editor-area').width();

            function _horizonal_split() {
                var h = Math.round(_height / 3);
                if (h > 400) h = 400;
                $scope.layout.viewstate.horizonal.lastComponentSize = h;
            }

            function _horizonal_top() {
                $scope.layout.viewstate.horizonal.lastComponentSize = 0;
            }

            if (layout == 1) {
                _horizonal_top();
                $scope.layout.viewstate.vertical_1_1.lastComponentSize = 0;
            } else if (layout == 2) {
                _horizonal_top();
                $scope.layout.viewstate.vertical_1_1.lastComponentSize = Math.round(_width / 2);
                $scope.layout.viewstate.vertical_1_2.lastComponentSize = 0;
            } else if (layout == 3) {
                _horizonal_top();
                $scope.layout.viewstate.vertical_1_1.lastComponentSize = Math.round(_width / 3 * 2);
                $scope.layout.viewstate.vertical_1_2.lastComponentSize = Math.round(_width / 3);
            } else if (layout == 4) {
                _horizonal_split();
                $scope.layout.viewstate.vertical_1_1.firstComponentSize = _width;
                $scope.layout.viewstate.vertical_1_1.lastComponentSize = 0;
            } else if (layout == 5) {
                _horizonal_split();
                $scope.layout.viewstate.vertical_1_1.firstComponentSize = Math.round(_width / 2);
                $scope.layout.viewstate.vertical_1_1.lastComponentSize = Math.round(_width / 2);
                $scope.layout.viewstate.vertical_1_2.firstComponentSize = Math.round(_width / 2);
                $scope.layout.viewstate.vertical_1_2.lastComponentSize = 0;
            } else if (layout == 6) {
                _horizonal_split();
                $scope.layout.viewstate.vertical_1_1.firstComponentSize = Math.round(_width / 3);
                $scope.layout.viewstate.vertical_1_1.lastComponentSize = Math.round(_width / 3 * 2);
                $scope.layout.viewstate.vertical_1_2.firstComponentSize = Math.round(_width / 3);
                $scope.layout.viewstate.vertical_1_2.lastComponentSize = Math.round(_width / 3);
            }

            await API.timeout();
        }
    }

    /*
     * define loading
     */
    BUILDER.loading = async () => {
        $scope.loading.status = true;
        $scope.loading.show = async () => {
            $scope.loading.status = true;
            await API.timeout();
        }

        $scope.loading.hide = async () => {
            $scope.loading.status = false;
            await API.timeout();
        }
    }

    /*
     * define modal events
     */

    BUILDER.modal = async () => {
        $scope.modal.delete = async () => {
            $('#modal-delete').modal('show');
        }

        $scope.modal.add_language = async () => {
            $('#modal-add-language').modal('show');
        }

        $scope.modal.keymaps = function () {
            $('#modal-keymaps').modal('show');
        }
    }

    /*
     * define workspace controller
     */

    BUILDER.workspace = async () => {
        $scope.workspace.list = [
            { id: 'app', name: 'App' },
            { id: 'browse', name: 'Browse' },
            { id: 'history', name: 'History' }
        ];

        $scope.workspace.list[0].active = async () => {
            $scope.workspace.active_workspace = $scope.workspace.list[0].id;
            await API.timeout();
        };

        $scope.workspace.list[1].active = async () => {
            $scope.workspace.active_workspace = $scope.workspace.list[1].id;

            await API.timeout();
        };

        $scope.workspace.list[2].active = async () => {
            $scope.workspace.active_workspace = $scope.workspace.list[2].id;

            if ($scope.viewer.selected) {
                await $scope.viewer.load($scope.viewer.selected);
            }

            await API.timeout();
        };

        $scope.workspace.active_workspace = $scope.workspace.list[0].id;
    }

    /*
     * define plugin interfaces for wiz
     */

    BUILDER.plugin = async () => {
        $scope.plugin.editor = {};
        $scope.plugin.editor.build = async (targettab, editor) => {
            let shortcuts = $scope.shortcut.configuration(window.monaco);

            for (let shortcutname in shortcuts) {
                let monacokey = shortcuts[shortcutname].monaco;
                let fn = shortcuts[shortcutname].fn;
                if (!monacokey) continue;

                editor.addCommand(monacokey, async () => {
                    await fn();
                    await $scope.shortcut.bind();
                });
            }
        }
    }

    /*
     * define app controller
     */

    BUILDER.app = {};

    BUILDER.app.base = async () => {
        $scope.app.save = async (returnres) => {
            if ($scope.app.data.controller) $scope.app.data.controller = $scope.app.data.controller.replace(/\t/gim, '    ');
            let appdata = angular.copy($scope.app.data);
            try {
                for (let key in appdata.dic) {
                    if (appdata.dic[key] && appdata.dic[key].length > 0) {
                        appdata.dic[key] = JSON.parse(appdata.dic[key]);
                    } else {
                        delete data.dic[key];
                    }
                }
            } catch (e) {
                if (!returnres)
                    toastr.error("Dictionary syntax error");
                return { code: 500, data: e };
            }

            try {
                $scope.browse.item.package.title = appdata.package.title;
                $scope.browse.item.package.namespace = appdata.package.namespace;
            } catch (e) {
            }

            let res = await API.update(appdata);

            if (returnres) return res;

            if (res.code == 200) {
                toastr.success("Saved");
                await $scope.app.preview();
            } else {
                toastr.error(res.data);
            }

            await $scope.shortcut.bind();
        }

        $scope.app.tab = {};
        $scope.app.tab.active = async (tab) => {
            $scope.app.tab.activetab = tab;
            await API.timeout();
        }

        $scope.app.delete = async () => {
            let app_id = $scope.app.id;
            await API.delete(app_id);
            await $scope.browse.load();
            if ($scope.browse.data[0]) {
                app_id = $scope.browse.data[0].package.id;
                location.href = APP_URL + "editor/" + app_id;
            } else {
                location.href = APP_URL;
            }
        }

        $scope.app.clean = async () => {
            let app_id = $scope.app.id;
            await API.clean(app_id);
            $scope.app.preview();
        }

        $scope.app.load = async (app_id) => {
            // show loading
            await $scope.loading.show();

            // load data
            let res = await API.load(app_id);
            $scope.app.id = app_id;  // current appid
            $scope.app.data = res.data;
            for (let key in $scope.app.data.dic) {
                $scope.app.data.dic[key] = JSON.stringify($scope.app.data.dic[key], null, 4);
            }

            await $scope.app.editor.build();
            await $scope.layout.change($scope.layout.active_layout);
            await $scope.loading.hide();
            await $scope.app.preview();

            await API.timeout(500);

            if ($scope.app.tab.activetab && $scope.app.editor.cache[$scope.app.tab.activetab])
                $scope.app.editor.cache[$scope.app.tab.activetab].focus();

            if ($scope.app.data.package.properties) {
                for (let key in $scope.app.data.package.properties) {
                    $scope.$watch('app.data.package.properties.' + key, async (a, b) => {
                        if (a == b) return;
                        await PROPERTY_WATCHER($scope, key);
                    });
                }
            }

            location.href = location.pathname + "#" + app_id;
        }

        $scope.app.preview = async () => {
            let url = $scope.app.data.package.viewuri;
            if (!$scope.app.data.package.viewuri) {
                url = await PREVIEW_URL($scope.app.id);
            }

            if (!url) {
                return;
            }

            $scope.app.preview.status = false;
            await API.timeout();

            $('iframe.preview').attr('src', url);
            $('iframe.preview').on('load', function () {
                $scope.app.preview.status = true;
                $timeout();
            });
        }
    }

    BUILDER.app.editor = async () => {
        $scope.app.editor = {};
        $scope.app.editor.cache = {};
        $scope.app.editor.properties = {};
        $scope.app.editor.codetypes = CODETYPES;
        $scope.app.editor.code = {};

        $scope.app.editor.code.list = CODELIST;

        $scope.app.editor.code.dic = {};
        $scope.app.editor.code.dic.add = async (lang) => {
            if (!lang || lang.length < 2) {
                toastr.error("at least 2 char");
                return;
            }
            lang = lang.toLowerCase();
            $scope.app.data.dic[lang] = "{}";
            $('#modal-add-language').modal('hide');
            await API.timeout();
        }

        $scope.app.editor.code.langselect = LANGSELECTOR($scope);

        $scope.app.editor.code.change = async (targettab, view) => {
            if (view) {
                $scope.configuration.tab[targettab + '_val'] = view;
                await API.timeout();

                if (view == 'preview') {
                    $scope.app.preview();
                    return;
                }

                if (view == 'debug') {
                    return;
                };

                let language = $scope.app.editor.properties[targettab].language = await $scope.app.editor.code.langselect(targettab);

                if ($scope.app.editor.cache[targettab]) {
                    let model = $scope.app.editor.cache[targettab].getModel();
                    monaco.editor.setModelLanguage(model, language);

                    $scope.app.editor.cache[targettab].focus();
                }
            } else {
                if ($scope.app.tab.activetab != targettab) {
                    $scope.app.tab.activetab = targettab;
                    await API.timeout();
                    await API.timeout(500);
                    $scope.app.editor.cache[targettab].focus();
                }
            }
        }

        $scope.app.editor.code.prev = async () => {
            if (!$scope.layout.accessable_tab) return;
            let tab = 'tab1';
            if ($scope.app.tab.activetab) tab = $scope.app.tab.activetab;

            tab = $scope.layout.accessable_tab.indexOf(tab) - 1;
            if (tab < 0) tab = $scope.layout.accessable_tab.length - 1;
            tab = $scope.layout.accessable_tab[tab];
            let view = $scope.configuration.tab[tab + '_val']

            while (view == 'preview') {
                tab = $scope.layout.accessable_tab.indexOf(tab) - 1;
                if (tab < 0) tab = $scope.layout.accessable_tab.length - 1;
                tab = $scope.layout.accessable_tab[tab];
                view = $scope.configuration.tab[tab + '_val']
            }

            $scope.app.editor.code.change(tab);
            $scope.app.editor.cache[tab].focus();
        }

        $scope.app.editor.code.next = async () => {
            if (!$scope.layout.accessable_tab) return;
            let tab = 'tab1';
            if ($scope.app.tab.activetab) tab = $scope.app.tab.activetab;

            tab = $scope.layout.accessable_tab.indexOf(tab) + 1;
            tab = tab % $scope.layout.accessable_tab.length;
            tab = $scope.layout.accessable_tab[tab];
            let view = $scope.configuration.tab[tab + '_val']

            while (view == 'preview') {
                tab = $scope.layout.accessable_tab.indexOf(tab) + 1;
                tab = tab % $scope.layout.accessable_tab.length;
                tab = $scope.layout.accessable_tab[tab];
                view = $scope.configuration.tab[tab + '_val']
            }

            $scope.app.editor.code.change(tab);
            $scope.app.editor.cache[tab].focus();
        }

        $scope.app.editor.build = async () => {
            $scope.app.editor.viewstate = false;
            await API.timeout();

            $scope.app.editor.properties.tab1 = $scope.monaco(await $scope.app.editor.code.langselect('tab1'));
            $scope.app.editor.properties.tab2 = $scope.monaco(await $scope.app.editor.code.langselect('tab2'));
            $scope.app.editor.properties.tab3 = $scope.monaco(await $scope.app.editor.code.langselect('tab3'));

            let bindonload = async (targettab) => {
                $scope.app.editor.properties[targettab].onLoad = async (editor) => {
                    await $scope.plugin.editor.build(targettab, editor);
                    $scope.app.editor.cache[targettab] = editor;
                }
            }

            for (var i = 1; i <= 3; i++)
                bindonload('tab' + i);

            $scope.app.editor.viewstate = true;
            await API.timeout();
        }

        $scope.app.branch = {};
        $scope.app.branch.change = async (branchname) => {
            let path = location.pathname.split("/");
            path = path.splice(0, path.length - 1);
            path.push($scope.app.id);
            path = path.join("/") + "?branch=" + branchname;
            location.href = path;
        }
    }

    BUILDER.browse = async () => {
        $scope.browse.load = async () => {
            let res = await API.search();
            $scope.browse.data = res.data;
            $scope.browse.cache = [];

            for (var i = 0; i < $scope.browse.data.length; i++) {
                $scope.browse.cache.push($scope.browse.data[i].package.id);
                if ($scope.browse.data[i].package.id == $scope.app.id) {
                    $scope.browse.item = $scope.browse.data[i];
                }
            }

            await API.timeout();
        }

        $scope.browse.select = async (item) => {
            $scope.browse.item = item;
            await $scope.app.load(item.package.id);
        }

        $scope.browse.search = async (val) => {
            val = val.toLowerCase();
            for (var i = 0; i < $scope.browse.data.length; i++) {
                let searchindex = ['title', 'namespace', 'id', 'route'];
                $scope.browse.data[i].hide = true;
                for (let j = 0; j < searchindex.length; j++) {
                    try {
                        let key = searchindex[j];
                        let keyv = $scope.browse.data[i].package[key].toLowerCase();
                        if (keyv.includes(val)) {
                            $scope.browse.data[i].hide = false;
                            break;
                        }
                    } catch (e) {
                    }
                }
                if (val.length == 0)
                    $scope.browse.data[i].hide = false;
            }

            await API.timeout();
        }

        $scope.browse.next = async () => {
            let current = $scope.browse.cache.indexOf($scope.app.id);
            current = current + 1;
            current = current % $scope.browse.data.length;
            $scope.browse.select($scope.browse.data[current]);
        }

        $scope.browse.prev = async () => {
            let current = $scope.browse.cache.indexOf($scope.app.id);
            current = current - 1;
            if (current < 0)
                current = $scope.browse.data.length - 1;
            $scope.browse.select($scope.browse.data[current]);
        }
    }


    BUILDER.history = async () => {
        $scope.history.load = async () => {
            $scope.history.data = await API.history();
            await API.timeout();
        }

        $scope.history.change = async (item) => {
            await $scope.viewer.load(item.id);
        }
    };

    BUILDER.viewer = async () => {
        $scope.viewer.editor = {};
        $scope.viewer.editor.data = {};

        $scope.viewer.editor.configuration = { enableSplitViewResizing: false, fontSize: 14, readOnly: false, originalEditable: false };
        $scope.viewer.editor.configuration.onLoad = async (editor) => {
            await $scope.plugin.editor.build(null, editor);
        }

        $scope.viewer.load = async (commit) => {
            await $scope.loading.show();
            let app_id = $scope.app.id;
            let compare = await API.diff(app_id, commit);

            $scope.viewer.codes = TABS;
            $scope.viewer.selected = commit;
            $scope.viewer.compared = compare;

            await $scope.viewer.change('controller');
        }

        $scope.viewer.change = async (code) => {
            $scope.viewer.code = code;

            let next = angular.copy($scope.app.data);
            let prev = angular.copy($scope.viewer.compared);

            for (let key in next.dic)
                next.dic[key] = JSON.parse(next.dic[key]);
            next.dic = JSON.stringify(next.dic, null, 4);

            try {
                next.language = "json";
                if (['controller', 'api', 'socketio'].includes(code)) next.language = "python";
                if (next.package.properties)
                    if (next.package.properties[code])
                        next.language = next.package.properties[code];
            } catch (e) {
                next.language = "text";
                next[code] = "";
            }

            try {
                prev.language = "json";
                if (['controller', 'api', 'socketio'].includes(code)) prev.language = "python";
                if ($scope.viewer.mode == 'app') if (prev.properties[code]) prev.language = prev.properties[code];
                if (prev.language == 'json') prev.code[code] = JSON.stringify(JSON.parse(prev.code[code]), null, 4);
            } catch (e) {
                prev.language = "text";
                prev.code[code] = "";
            }

            $scope.viewer.editor.data = {
                compare: {
                    code: prev.code[code],
                    language: prev.language
                },
                main: {
                    code: next[code],
                    language: next.language
                }
            }

            await $scope.loading.hide();
            await API.timeout();
        }

        $scope.$watch('viewer.editor.data', function () {
            let code = $scope.viewer.code;
            if (!code) return;
            let codedata = $scope.viewer.editor.data.main.code;
            if (code == 'dic') {
                try {
                    codedata = JSON.parse(codedata);
                    for (let key in codedata) {
                        codedata[key] = JSON.stringify(codedata[key], null, 4);
                    }
                } catch (e) {
                    return;
                }
            }

            if (codedata != $scope.app.data[code])
                $scope.app.data[code] = codedata;
        }, true);
    };

    BUILDER.shortcuts = async () => {
        $scope.shortcut.configuration = (monaco) => {
            return {
                'tab1': {
                    key: 'Alt Digit1',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.DIGIT1,
                    fn: async () => {
                        await $scope.workspace.list[0].active();
                    }
                },
                'tab2': {
                    key: 'Alt Digit2',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.DIGIT2,
                    fn: async () => {
                        await $scope.workspace.list[1].active();
                    }
                },
                'tab3': {
                    key: 'Alt Digit3',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.DIGIT3,
                    fn: async () => {
                        await $scope.workspace.list[2].active();
                    }
                },
                'editor_prev': {
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_A,
                    fn: async () => {
                        let targettab = $scope.app.tab.activetab;
                        var prev = TABS.indexOf($scope.configuration.tab[targettab + "_val"]) - 1;
                        if (prev < 0) prev = TABS[TABS.length - 1];
                        else prev = TABS[prev];

                        if (prev == 'preview') {
                            prev = TABS.indexOf(prev) - 1;
                            if (prev < 0) prev = TABS[TABS.length - 1];
                            else prev = TABS[prev];
                        }

                        await $scope.app.editor.code.change(targettab, prev);
                        await $scope.shortcut.bind();
                    }
                },
                'editor_next': {
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_S,
                    fn: async () => {
                        let targettab = $scope.app.tab.activetab;
                        var next = TABS[(TABS.indexOf($scope.configuration.tab[targettab + "_val"]) + 1) % TABS.length];
                        if (next == 'preview') {
                            next = TABS[(TABS.indexOf(next) + 1) % TABS.length];
                        }
                        await $scope.app.editor.code.change(targettab, next);
                        await $scope.shortcut.bind();
                    }
                },
                'app_prev': {
                    key: 'Alt KeyJ',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_J,
                    fn: async () => {
                        $(window).focus();
                        await $scope.browse.prev();
                    }
                },
                'app_next': {
                    key: 'Alt KeyK',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_K,
                    fn: async () => {
                        $(window).focus();
                        await $scope.browse.next();
                    }
                },
                'workspace_prev': {
                    key: 'Alt KeyZ',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_Z,
                    fn: async () => {
                        await $scope.app.editor.code.prev();
                    }
                },
                'workspace_next': {
                    key: 'Alt KeyX',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_X,
                    fn: async () => {
                        await $scope.app.editor.code.next();
                    }
                },
                'search': {
                    key: 'Alt KeyF',
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_F,
                    fn: async () => {
                        await $scope.workspace.list[1].active();
                        $('#search').focus();
                    }
                },
                'save': {
                    key: 'Ctrl KeyS',
                    monaco: monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S,
                    fn: async () => {
                        await $scope.app.save();
                    }
                },
                'clear': {
                    key: 'Ctrl KeyK',
                    monaco: monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_K,
                    fn: async () => {
                        await $scope.socket.clear();
                    }
                }
            }
        };

        $scope.shortcut.bind = async () => {
            if (!window.monaco) return;
            $(window).unbind();

            let shortcut_opts = {};
            let shortcuts = $scope.shortcut.configuration(window.monaco);
            for (let key in shortcuts) {
                let keycode = shortcuts[key].key;
                let fn = shortcuts[key].fn;
                if (!keycode) continue;
                shortcut_opts[keycode] = async (ev) => {
                    ev.preventDefault();
                    await fn();
                };
            }

            shortcutjs(window, shortcut_opts);
        }

        window.addEventListener("focus", $scope.shortcut.bind, false);
    }

    await BUILDER.loading();
    await BUILDER.layout();
    await BUILDER.plugin();
    await BUILDER.modal();
    await BUILDER.workspace();
    await BUILDER.app.base();
    await BUILDER.app.editor();
    await BUILDER.browse();
    await BUILDER.history();
    await BUILDER.viewer();
    await BUILDER.shortcuts();

    let init = async () => {
        await ADDON($scope);
        await $scope.browse.load();
        await $scope.history.load();
        await $scope.app.load(APPID);

        /*
         * socket.io event binding for trace log
         */
        let ansi_up = new AnsiUp();
        let socket = io("/wiz");

        $scope.socket.log = "";
        $scope.socket.clear = async () => {
            $scope.socket.log = "";
            await API.timeout();
        }

        $scope.socket.link = async () => {
            let layout = $scope.configuration.layout;
            await $scope.layout.change(layout - 3);
            window.open("/wiz/admin/workspace/logger", '_blank');
        }

        socket.on("connect", function (data) {
            if (!data) return;
            $scope.socket.id = data.sid;
        });

        socket.on("log", function (data) {
            data = data.replace(/ /gim, "__SEASONWIZPADDING__");
            data = ansi_up.ansi_to_html(data).replace(/\n/gim, '<br>').replace(/__SEASONWIZPADDING__/gim, '<div style="width: 6px; display: inline-block;"></div>');
            $scope.socket.log = $scope.socket.log + data;
            $timeout(function () {
                var element = $('.debug-messages')[0];
                if (!element) return;
                element.scrollTop = element.scrollHeight - element.clientHeight;
            });
        });

        socket.on("message", function (data) {
            if (data.type == "status") {
                $scope.socket.users = data.users;
                $timeout();
            }
        });

        $scope.$watch("configuration", async () => {
            let layout = $scope.configuration.layout;
            if (layout < 4) {
                socket.emit("leave", { id: BRANCH });
            } else {
                socket.emit("join", { id: BRANCH });
            }
        }, true);
    }

    init();
};