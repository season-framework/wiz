const LOCALSTORAGEID = "season.wiz.branch.configuration";
const API_URL = "/wiz/admin/branch/commit/api";
const COMMIT_ID = location.hash.split("#")[1] ? location.hash.split("#")[1] : '';

let content_controller = async ($scope, $timeout, $sce) => {
    _builder($scope, $timeout);

    /*
     * define variables
     */
    let BUILDER = {};

    let API = {
        handler: (resolve, reject) => async (res) => {
            if (res.code == 200) resolve(res.data);
            else reject(res);
        },
        diff: () => new Promise((resolve, reject) => {
            let url = API_URL + '/diff/' + TARGET_BRANCH + "/" + COMMIT_ID;
            $.get(url, API.handler(resolve, reject));
        }),
        history: () => new Promise((resolve, reject) => {
            let url = API_URL + '/history/' + TARGET_BRANCH;
            $.get(url, API.handler(resolve, reject));
        }),
        file: (filepath, commit) => new Promise((resolve, reject) => {
            if (!commit) commit = "";
            let url = API_URL + '/file/' + TARGET_BRANCH + "/" + commit;
            $.post(url, { filepath: filepath }, API.handler(resolve, reject));
        }),
        commit: (message) => new Promise((resolve, reject) => {
            let url = API_URL + '/commit/' + TARGET_BRANCH;
            $.post(url, { message: message }, API.handler(resolve, reject));
        }),
        update: (data) => new Promise((resolve, reject) => {
            data = angular.copy(data);
            let url = API_URL + '/update/' + TARGET_BRANCH;
            $.post(url, data, API.handler(resolve, reject));
        }),
        timeout: (ts) => new Promise((resolve, reject) => {
            $timeout(resolve, ts);
        })
    };

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
    $scope.commit = {};                 // controller for code editor
    $scope.history = {};              // controller for code editor
    $scope.viewer = {};              // controller for code editor
    $scope.shortcut = {};
    $scope.socket = {};

    /* 
     * load wiz editor options from localstorage
     */
    try {
        let configuration = JSON.parse(localStorage[LOCALSTORAGEID]);
        try { delete configuration.layout.opts.root.lastComponentSize; } catch (e) { }
        $scope.configuration = configuration;
    } catch (e) {
        $scope.configuration = {};
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
    }

    /*
     * define workspace controller
     */

    BUILDER.workspace = async () => {
        $scope.workspace.list = [
            { id: 'commit', name: 'Commit' },
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

        $scope.workspace.active_workspace = $scope.workspace.list[0].id;
    }

    /*
     * define plugin interfaces for wiz
     */

    BUILDER.plugin = async () => {
        $scope.plugin.editor = {};
        $scope.plugin.editor.build = async (editor) => {
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
     * define commit controller
     */

    BUILDER.commit = async () => {
        $scope.commit.load = async () => {
            $scope.commit.files = await API.diff();
            await API.timeout();
        }

        $scope.commit.commit = async (message) => {
            if (!message) message = 'commit';
            await API.commit(message);
            location.reload();
        }

        $scope.commit.id = COMMIT_ID;
    };

    BUILDER.history = async () => {
        $scope.history.load = async () => {
            $scope.history.data = await API.history();
            await API.timeout();
        }

        $scope.history.change = async (item) => {
            if (item.id == $scope.commit.id) {
                return;
            }

            let path = location.pathname + "#" + item.id;
            location.href = path;
            location.reload();
        }
    };

    BUILDER.viewer = async () => {
        $scope.viewer.editor = {};
        $scope.viewer.editor.configuration = { enableSplitViewResizing: false, fontSize: 14, readOnly: COMMIT_ID != '', originalEditable: false };

        $scope.viewer.editor.configuration.onLoad = async (editor) => {
            await $scope.plugin.editor.build(editor);
        }

        $scope.viewer.load = async (obj) => {
            if (!obj) return;

            await $scope.loading.show();

            let monaco_data = null;

            try {
                $scope.viewer.editor.configuration = { enableSplitViewResizing: false, fontSize: 14, readOnly: COMMIT_ID != '', originalEditable: false };

                $scope.viewer.editor.configuration.onLoad = async (editor) => {
                    await $scope.plugin.editor.build(editor);
                }

                let next = await API.file(obj.commit_path, obj.commit == 'index' ? null : obj.commit);
                let prev = await API.file(obj.parent_path, obj.parent == 'index' ? null : obj.parent);

                if (next.mode == 'apps') {
                    next = next.app;
                    prev = prev.app;

                    $scope.viewer.appdata = { prev: prev, next: next };
                    $scope.viewer.mode = 'app';
                    $scope.viewer.codes = ['info', 'controller', 'api', 'socketio', 'html', 'js', 'css', 'dic'];
                } else if (next.mode == 'routes') {
                    next = next.app;
                    prev = prev.app;

                    $scope.viewer.appdata = { prev: prev, next: next };
                    $scope.viewer.mode = 'route';
                    $scope.viewer.codes = ['info', 'controller', 'dic'];
                } else {
                    $scope.viewer.appdata = null;
                    $scope.viewer.mode = 'file';
                    $scope.viewer.codes = [];
                    monaco_data = {
                        compare: {
                            code: prev.text,
                            language: prev.language
                        },
                        main: {
                            code: next.text,
                            language: next.language
                        }
                    }
                }
            } catch (e) {
                $scope.viewer.editor.configuration = { enableSplitViewResizing: false, fontSize: 14, readOnly: true, originalEditable: false };

                $scope.viewer.editor.configuration.onLoad = async (editor) => {
                    await $scope.plugin.editor.build(editor);
                }

                $scope.viewer.appdata = null;
                $scope.viewer.mode = 'etc';
                $scope.viewer.codes = [];
                monaco_data = {
                    compare: {
                        code: obj.parent_path,
                        language: 'text'
                    },
                    main: {
                        code: obj.commit_path,
                        language: 'text'
                    }
                }
            }

            $scope.viewer.selected = obj;

            await $scope.loading.hide();

            if (monaco_data) {
                $scope.viewer.editor.data = monaco_data;
                await API.timeout();
            } else {
                await $scope.viewer.change('info');
            }
        }

        $scope.viewer.update = async () => {
            if ($scope.viewer.mode == 'etc') return;
            let data = angular.copy($scope.viewer.selected);
            let code = angular.copy($scope.viewer.editor.data.main).code;
            let path = data.commit_path;

            if ($scope.viewer.mode == 'file') {
                await API.update({ data: code, path: path });
                toastr.success("Saved");
                return;
            }

            let codemap = {};
            codemap.info = 'app.json';
            codemap.controller = 'controller.py';
            codemap.api = 'api.py';
            codemap.socketio = 'socketio.py';
            codemap.html = 'html.dat';
            codemap.js = 'js.dat';
            codemap.css = 'css.dat';
            codemap.dic = 'dic.json';

            if (!codemap[$scope.viewer.code]) {
                return;
            }

            path = path + "/" + codemap[$scope.viewer.code];
            await API.update({ data: code, path: path });
            toastr.success("Saved");
        }

        $scope.viewer.change = async (code) => {
            if (!$scope.viewer.appdata) return;
            $scope.viewer.code = code;

            let { next, prev } = angular.copy($scope.viewer.appdata);

            try {
                next.language = "json";
                if (['controller', 'api', 'socketio'].includes(code)) next.language = "python";
                if ($scope.viewer.mode == 'app') if (next.properties[code]) next.language = next.properties[code];
                if (next.language == 'json') next[code] = JSON.stringify(JSON.parse(next[code]), null, 4);
            } catch (e) {
                next.language = "text";
                next[code] = "";
            }

            try {
                prev.language = "json";
                if (['controller', 'api', 'socketio'].includes(code)) prev.language = "python";
                if ($scope.viewer.mode == 'app') if (prev.properties[code]) prev.language = prev.properties[code];
                if (prev.language == 'json') prev[code] = JSON.stringify(JSON.parse(prev[code]), null, 4);
            } catch (e) {
                prev.language = "text";
                prev[code] = "";
            }

            $scope.viewer.editor.data = {
                compare: {
                    code: prev[code],
                    language: prev.language
                },
                main: {
                    code: next[code],
                    language: next.language
                }
            }

            await API.timeout();
        }
    };

    BUILDER.shortcuts = async () => {
        $scope.shortcut.configuration = (monaco) => {
            if (!monaco) monaco = { KeyMod: {}, KeyCode: {} };
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
                'editor_prev': {
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_A,
                    fn: async () => {
                        let TABS = angular.copy($scope.viewer.codes);
                        let prev = TABS.indexOf($scope.viewer.code) - 1;
                        if (prev < 0) prev = TABS[TABS.length - 1];
                        else prev = TABS[prev];
                        await $scope.viewer.change(prev);
                        await $scope.shortcut.bind();
                    }
                },
                'editor_next': {
                    monaco: monaco.KeyMod.Alt | monaco.KeyCode.KEY_S,
                    fn: async () => {
                        let TABS = angular.copy($scope.viewer.codes);
                        var next = TABS[(TABS.indexOf($scope.viewer.code) + 1) % TABS.length];
                        await $scope.viewer.change(next);
                        await $scope.shortcut.bind();
                    }
                },
                'save': {
                    key: 'Ctrl KeyS',
                    monaco: monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S,
                    fn: async () => {
                        await $scope.viewer.update();
                    }
                }
            }
        };

        $scope.shortcut.bind = async () => {
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

        await $scope.shortcut.bind();

        window.addEventListener("focus", $scope.shortcut.bind, false);
    }

    BUILDER.layout();
    BUILDER.plugin();
    BUILDER.loading();
    BUILDER.modal();
    BUILDER.workspace();
    BUILDER.commit();
    BUILDER.history();
    BUILDER.viewer();
    BUILDER.shortcuts();

    $scope.extdata = {};
    $scope.extdata.branch = TARGET_BRANCH;
    $scope.extdata.branches = BRANCHES;
    $scope.extdata.change_branch = async (branchname) => {
        location.href = "/wiz/admin/branch/commit/diff/" + branchname;
    }

    await $scope.commit.load();
    await $scope.history.load();
    await $scope.loading.hide();

    await API.timeout();
};