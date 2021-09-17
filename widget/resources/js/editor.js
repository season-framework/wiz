var content_controller = function ($scope, $timeout, $sce) {
    _builder($scope, $timeout);
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
            $scope.event.save();
        });
    }


    var API_URL = "/wiz/widget";
    var API = {
        INFO: API_URL + '/api/info/' + app_id,
        DELETE: API_URL + '/api/delete',
        UPDATE: API_URL + '/api/update/' + app_id,
        UPLOAD: API_URL + '/api/upload',
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

    try {
        $scope.options = JSON.parse(localStorage["season.wiz.option"])
    } catch (e) {
        $scope.options = {};
        $scope.options.layout = 2;
        $scope.options.tab = {};
        $scope.options.tab['tab1_val'] = 'html';
        $scope.options.tab['tab2_val'] = 'readme';
        $scope.options.tab['tab5_val'] = 'preview';
        $scope.options.infotab = 1;
        $scope.options.sidemenu = true;
    }

    $scope.$watch("options", function () {
        var opt = angular.copy($scope.options);
        localStorage["season.wiz.option"] = JSON.stringify(opt);
    }, true);

    $scope.event = {};

    $.get(API.INFO, function (res) {
        $scope.info = res.data;
        if (!$scope.info.theme) {
            $scope.info.theme = "default";
        }
        $scope.event.iframe();
        $timeout();
    });

    $scope.event.delete = function () {
        $.get(API.DELETE, { app_id: app_id }, function (res) {
            location.href = API.LIST + "/list/" + $scope.info.category;
        });
    }

    $scope.event.modal = {};
    $scope.event.modal.delete = function () {
        $('#modal-delete').modal('show');
    }

    $scope.event.iframe = function (findurl) {
        var url = API.IFRAME(app_id, app_id);
        if (findurl) {
            return url;
        }
        $timeout(function () {
            $('iframe.preview').attr('src', url);
        });
    };

    $scope.event.save = function (cb) {
        $scope.info.html = $scope.info.html.replace(/\t/gim, '    ');
        $scope.info.css = $scope.info.css.replace(/\t/gim, '    ');
        $scope.info.js = $scope.info.js.replace(/\t/gim, '    ');
        $scope.info.api = $scope.info.api.replace(/\t/gim, '    ');
        $scope.info.kwargs = $scope.info.kwargs.replace(/\t/gim, '    ');

        var data = angular.copy($scope.info);

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

    // shortcut
    shortcutjs(window, {
        'control s': function (ev) {
            ev.preventDefault();
            $scope.event.save();
        },
        'default': function (ev, name) { }
    });

    // drag event
    var dragbasewidth = 0;
    var dragbaseheight = 0;
    var vh50 = window.innerHeight / 2;
    $scope.status_drag = '';
    $scope.event.drag = {
        onstart: function (self) {
            $scope.status_drag = 'unselectable';
            $timeout();

            vh50 = window.innerHeight / 2;

            var target = $(self.element).attr('target');
            dragbasewidth = $('.' + target).width();

            var tds = $('.code-top td.bg-white');
            for (var i = 0; i < tds.length; i++) {
                var w = $(tds[i]).width();
                if (i == tds.length - 1) {
                    $(tds[i]).width('auto');
                } else {
                    $(tds[i]).width(w);
                }
            }

            var tds = $('.code-tabs-top td');
            for (var i = 0; i < tds.length; i++) {
                var w = $(tds[i]).width();
                if (i == tds.length - 1) {
                    $(tds[i]).width('auto');
                } else {
                    $(tds[i]).width(w);
                }
            }

            if ($scope.options.layout < 5) return;
            dragbaseheight = $('.tab-5').height();
        },
        onmove: function (self, pos) {
            var target = $(self.element).attr('target');

            if (target == 'tab-5') {
                var move_y = pos.y;
                var resize_h = dragbaseheight - move_y - 1;
                var base_h = vh50 - 65;
                var diff = base_h - resize_h;
                var hstr = 'calc(100vh - 130px - ' + resize_h + 'px)';
                $('.code-top td').height(hstr);
                hstr = 'calc(100vh - 132px - ' + resize_h + 'px)';
                $('.code-top td .code-input').height(hstr);
                $('.code-top td .code-input .CodeMirror').height(hstr);

                $('.code-bottom td').height(resize_h);
                $('.code-bottom td .code-input').height(resize_h);
                $('.code-bottom td .code-input .CodeMirror').height(resize_h);

                return;
            }

            var move_x = pos.x;

            if (dragbasewidth + move_x - 1 < 400) return;
            if (move_x > 0 && $('.code-top td.bg-white:last-child').width() < 400) {
                return;
            }

            $('.' + target).width(dragbasewidth + move_x - 1);
        },
        onend: function (self) {
            $scope.status_drag = '';
            $timeout();
        }
    };

    $timeout(function () {
        if ($scope.options.layout > 4) {
            var resize_h = 300;
            var hstr = 'calc(100vh - 130px - ' + resize_h + 'px)';
            $('.code-top td').height(hstr);
            hstr = 'calc(100vh - 132px - ' + resize_h + 'px)';
            $('.code-top td .code-input').height(hstr);
            $('.code-top td .code-input .CodeMirror').height(hstr);

            $('.code-bottom td').height(resize_h);
            $('.code-bottom td .code-input').height(resize_h);
            $('.code-bottom td .code-input .CodeMirror').height(resize_h);
        }
    })

    $scope.$watch('options.tab', function () {
        try {
            var hstr = $('.code-top td')[0].style.height;
            $timeout(function () {
                $('.h-half .code-top td .code-input').height(hstr);
                $('.h-half .code-top td .code-input .CodeMirror').height(hstr);
            });
        } catch (e) { }
    }, true);

    $scope.event.toggle = {};
    $scope.event.toggle.sidemenu = function () {
        $scope.options.sidemenu = !$scope.options.sidemenu;
        $timeout();
    }
};