var json_array_parse = function (val, defaultvalue) {
    try {
        return JSON.parse(val);
    } catch (e) {
        if (defaultvalue)
            return defaultvalue;
    }
    return val;
}

var _builder = function ($scope, $timeout) {
    $scope.modal = {};
    $scope.modal.alert = function (message) {
        $scope.modal.color = 'btn-danger';
        $scope.modal.message = message;
        $('#modal-alert').modal('show');
        $timeout();
    }

    $scope.modal.success = function (message) {
        $scope.modal.color = 'btn-primary'
        $scope.modal.message = message;
        $('#modal-alert').modal('show');
        $timeout();
    }

    $scope.monaco = function (language) {
        var opt = {
            value: '',
            language: language,
            theme: "vs",
            fontSize: 14,
            automaticLayout: true 
        };

        return opt;
    }

    $scope.tinymce = function (options) {
        var opt = {
            // language_url: "/resources/wiz/theme/lang/tinymce/ko_KR.js",
            // language: "ko_KR",
            plugins: 'print preview paste searchreplace autolink directionality code visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists wordcount imagetools textpattern noneditable help charmap emoticons',
            menubar: false,
            statusbar: false,
    
            toolbar: 'formatselect | h2 h3 h4 | fontsizeselect forecolor backcolor bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | table hr image link code',
            toolbar_sticky: true,

            height: "100%",
    
            image_advtab: true,
            importcss_append: true,
            image_title: true,
            image_caption: true,
            automatic_uploads: true,
    
            file_picker_types: 'image',
            file_picker_callback: function(cb, value, meta) {
                var input = document.getElementById(options.input);
                input.onchange = function() {
                    var form_data = new FormData($(options.form)[0]);
    
                    $.ajax({
                        url: options.url,
                        type: 'POST',
                        xhr: function() {
                            var myXhr = $.ajaxSettings.xhr();
                            if (myXhr.upload) {
                                myXhr.upload.addEventListener('progress', function(event) {
                                    var percent = 0;
                                    var position = event.loaded || event.position;
                                    var total = event.total;
                                    if (event.lengthComputable) {
                                        percent = Math.round(position / total * 10000) / 100;
                                    }
                                }, false);
                            }
                            return myXhr;
                        },
                        data: form_data,
                        cache: false,
                        contentType: false,
                        processData: false
                    }).always(function(res) {
                        if (options.after_upload) {
                            options.after_upload(res.data, cb);
                            return;
                        }
    
                        for (var i = 0; i < res.data.length; i++) {
                            var uri = res.data[i];
                            cb(uri, { width: '100%', height: null });
                        }
                    });
                };
                input.click();
            },
    
            codesample_languages: [
                { text: 'Bash', value: 'bash' },
                { text: 'HTML/XML', value: 'markup' },
                { text: 'JavaScript', value: 'javascript' },
                { text: 'CSS', value: 'css' },
    
                { text: 'Apache Conf', value: 'apacheconf' },
                { text: 'PHP', value: 'php' },
                { text: 'Python', value: 'python' },
    
                { text: 'SQL', value: 'sql' },
    
                { text: 'Java', value: 'java' },
                { text: 'C', value: 'c' },
                { text: 'C#', value: 'csharp' },
                { text: 'C++', value: 'cpp' },
                { text: 'Ruby', value: 'ruby' },
            ],
    
            relative_urls: false,
    
            quickbars_selection_toolbar: 'styleselect | bold italic | quicklink h2 h3 blockquote quickimage quicktable',
            noneditable_noneditable_class: 'mceNonEditable',
            toolbar_mode: 'wrap',
    
            contextmenu: 'link image imagetools table',
            skin: 'oxide',
            content_css: '/resources/wiz/theme/libs/fontawesome/css/all.min.css,/resources/wiz/theme/libs/tabler/dist/css/tabler.min.css,/resources/wiz/theme/libs/tabler/dist/css/tabler-flags.min.css,/resources/wiz/theme/libs/tabler/dist/css/tabler-payments.min.css,/resources/wiz/theme/libs/tabler/dist/css/tabler-buttons.min.css,/resources/wiz/theme/libs/tabler/dist/css/demo.min.css,/resources/wiz/theme/less/theme.less',
            content_style: options.css ? options.css : 'body {max-width: 1024px; padding: 32px !important; background: white;} ul {margin: 0;}'
        };

        return opt;
    }
}

var cache_builder = function (version) {
    return {
        get: function (_default) {
            return json_array_parse(localStorage[version], _default);
        },
        update: function (value) {
            localStorage[version] = JSON.stringify(angular.copy(value));
        },
        claer: function () {
            delete localStorage[version];
        }
    };
}

try {
    app.controller('content', content_controller);
} catch (e) {
    app.controller('content', function () { });
}