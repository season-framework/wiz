toastr.options = {
    "closeButton": false,
    "debug": false,
    "newestOnTop": false,
    "progressBar": false,
    "positionClass": "toast-top-left",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": 300,
    "hideDuration": 1000,
    "timeOut": 5000,
    "extendedTimeOut": 1000,
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
}

;
(function(global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' &&
        typeof require === 'function' ? factory(require('../moment')) :
        typeof define === 'function' && define.amd ? define(['../moment'], factory) :
        factory(global.moment)
}(this, (function(moment) {
    'use strict';

    //! moment.js locale configuration

    var ko = moment.updateLocale('ko', {
        months: '1월_2월_3월_4월_5월_6월_7월_8월_9월_10월_11월_12월'.split('_'),
        monthsShort: '1월_2월_3월_4월_5월_6월_7월_8월_9월_10월_11월_12월'.split(
            '_'
        ),
        weekdays: '일요일_월요일_화요일_수요일_목요일_금요일_토요일'.split('_'),
        weekdaysShort: '일_월_화_수_목_금_토'.split('_'),
        weekdaysMin: '일_월_화_수_목_금_토'.split('_'),
        longDateFormat: {
            LT: 'A h:mm',
            LTS: 'A h:mm:ss',
            L: 'YYYY.MM.DD.',
            LL: 'YYYY년 MMMM D일',
            LLL: 'YYYY년 MMMM D일 A h:mm',
            LLLL: 'YYYY년 MMMM D일 dddd A h:mm',
            l: 'YYYY.MM.DD.',
            ll: 'YYYY년 MMMM D일',
            lll: 'YYYY년 MMMM D일 A h:mm',
            llll: 'YYYY년 MMMM D일 dddd A h:mm',
        },
        calendar: {
            sameDay: '오늘 LT',
            nextDay: '내일 LT',
            nextWeek: 'dddd LT',
            lastDay: '어제 LT',
            lastWeek: '지난주 dddd LT',
            sameElse: 'L',
        },
        relativeTime: {
            future: '%s 후',
            past: '%s 전',
            s: '몇 초',
            ss: '%d초',
            m: '1분',
            mm: '%d분',
            h: '한 시간',
            hh: '%d시간',
            d: '하루',
            dd: '%d일',
            M: '한 달',
            MM: '%d달',
            y: '일 년',
            yy: '%d년',
        },
        dayOfMonthOrdinalParse: /\d{1,2}(일|월|주)/,
        ordinal: function(number, period) {
            switch (period) {
                case 'd':
                case 'D':
                case 'DDD':
                    return number + '일';
                case 'M':
                    return number + '월';
                case 'w':
                case 'W':
                    return number + '주';
                default:
                    return number;
            }
        },
        meridiemParse: /AM|PM/,
        isPM: function(token) {
            return token === 'PM';
        },
        meridiem: function(hour, minute, isUpper) {
            return hour < 12 ? 'AM' : 'PM';
        },
    });

    return ko;
})));

Number.prototype.format = function() {
    if (this == 0) return 0;
    var reg = /(^[+-]?\d+)(\d{3})/;
    var n = (this + '');
    while (reg.test(n)) n = n.replace(reg, '$1' + ',' + '$2');
    return n;
};

String.prototype.number_format = function() {
    var num = parseFloat(this);
    if (isNaN(num)) return "0";

    return num.format();
};

Array.prototype.remove = function() {
    var what, a = arguments,
        L = a.length,
        ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};

String.prototype.string = function(len) {
    var s = '',
        i = 0;
    while (i++ < len) { s += this; }
    return s;
};
String.prototype.zf = function(len) { return "0".string(len - this.length) + this; };
Number.prototype.zf = function(len) { return this.toString().zf(len); };

Date.prototype.format = function(f) {
    if (!this.valueOf()) return " ";

    var weekName = ["일요일", "월요일", "화요일", "수요일", "목요일", "금요일", "토요일"];
    var d = this;

    return f.replace(/(yyyy|yy|MM|dd|E|hh|mm|ss|a\/p)/gi, function($1) {
        switch ($1) {
            case "yyyy":
                return d.getFullYear();
            case "yy":
                return (d.getFullYear() % 1000).zf(2);
            case "MM":
                return (d.getMonth() + 1).zf(2);
            case "dd":
                return d.getDate().zf(2);
            case "E":
                return weekName[d.getDay()];
            case "HH":
                return d.getHours().zf(2);
            case "hh":
                return ((h = d.getHours() % 12) ? h : 12).zf(2);
            case "mm":
                return d.getMinutes().zf(2);
            case "ss":
                return d.getSeconds().zf(2);
            case "a/p":
                return d.getHours() < 12 ? "AM" : "PM";
            default:
                return $1;
        }
    });
};

var calc_working_time = function(st, et) {
    if (!st) return 0;

    var today = moment().format('YYYY-MM-DD');
    var tday = moment(st).format('YYYY-MM-DD');

    var lst = new Date(moment(st).format('YYYY-MM-DD 12:00:00')).getTime(); // 점심시간
    var wet = new Date(moment(st).format('YYYY-MM-DD 22:00:00')).getTime(); // 업무종료시간

    st = st.getTime();

    if (et) {
        et = et.getTime();
    } else if (today == tday) {
        et = new Date().getTime();
    } else {
        et = wet;
    }

    if (et > wet) et = wet;

    var minus = 0;
    if (st <= lst) {
        minus = (et - lst) / 1000 / 60 / 60;
        if (minus > 1) {
            minus = 1;
        }
    }
    if (minus < 0) minus = 0;

    var t = Math.round(((et - st) / 1000 / 60 / 60 - minus) * 100) / 100;
    return t;
}

var get_working_time = function(worklog) {
    var working_time = 0;
    var st = null;

    var lst = new Date(moment().format('YYYY-MM-DD 12:00:00')).getTime();
    var
    let = new Date(moment().format('YYYY-MM-DD 13:00:00')).getTime();

    for (var i = 0; i < worklog.length; i++) {
        var wl = worklog[i];
        var wt = wl.log_type;
        var ct = new Date().getTime();

        var calc = false;
        if (wt == 'in') {
            st = new Date(wl.timestamp).getTime();
            if (i == worklog.length - 1) {
                calc = true;
            }
        } else {
            calc = true;
        }

        if (calc) {
            if (!st) st = new Date(moment().format('YYYY-MM-DD 00:00:00')).getTime();
            var et = new Date(wl.timestamp).getTime();
            if (wt == 'in') {
                et = ct;
            }

            working_time += et - st;

            if (st <= lst) {
                if (et >= lst) {
                    var minus = (et - lst);
                    if (minus > 1000 * 60 * 60) {
                        minus = 1000 * 60 * 60;
                    }
                    working_time -= minus;
                }
            }

            st = et;
        }
    }

    return working_time;
}

var calc_worklog = function(worklog) {
    var wl_tmp = {};
    var wlog = [];
    for (var i = 0; i < worklog.length; i++) {
        var wl = worklog[i];
        if (wl.type) continue;
        var wt = wl.log_type;
        var td = moment(wl.timestamp).format('YYYY-MM-DD');

        if (wt == 'in') {
            if (wl_tmp.day && wl_tmp.day != td) {
                wlog.push(wl_tmp);
            } else if (wl_tmp.day) {
                continue;
            }

            wl_tmp = {};
            wl_tmp.in = wl.timestamp;
            wl_tmp.in_ip = wl.ip;
            wl_tmp.day = td;

            if (worklog.length - 1 == i)
                wlog.push(wl_tmp);
        } else {
            if (wl_tmp.day != td) {
                wlog.push(wl_tmp);
                wl_tmp = {};
            }

            wl_tmp.out = wl.timestamp;
            wl_tmp.out_ip = wl.ip;
            wl_tmp.day = td;
            wlog.push(wl_tmp);
            wl_tmp = {};
        }
    }

    var daily_worktime = {};
    for (var i = 0; i < wlog.length; i++) {
        var day = wlog[i].day;
        if (!daily_worktime[day]) daily_worktime[day] = 0;
        var st = wlog[i].in;
        var et = wlog[i].out;
        if (!st) {
            wlog.working_time = 0;
            continue;
        }

        st = new Date(st);
        if (et) et = new Date(et);

        var wt = calc_working_time(st, et);
        if (!et & day != moment().format('YYYY-MM-DD')) {
            var remain = 8 - daily_worktime[day];
            if (remain < 0) remain = 0;
            if (remain > 3) remain = 3;

            if (wt > remain) {
                wt = remain;
            }
        }

        wlog[i].working_time = wt;
        daily_worktime[day] += wlog[i].working_time;
    }

    return wlog;
}

function commute_event() {
    $.get("/mydesk/api/commute_log", function(res) {
        if (res.status) {
            location.reload();
            return;
        }

        toastr.error(res.message);
    });
};

var get_tinymce_opt = function(selector, options) {
    return {
        language_url: "/resources/theme/lang/tinymce/ko_KR.js",
        language: "ko_KR",
        selector: selector,
        plugins: 'print preview paste searchreplace autolink directionality code visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists wordcount imagetools textpattern noneditable help charmap emoticons autoresize',
        menubar: false,

        toolbar: 'formatselect | h2 h3 h4 | fontsizeselect forecolor backcolor bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist | table hr image link code',
        toolbar_sticky: true,

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

        autoresize_bottom_margin: 50,
        relative_urls: false,

        quickbars_selection_toolbar: 'styleselect | bold italic | quicklink h2 h3 blockquote quickimage quicktable',
        noneditable_noneditable_class: 'mceNonEditable',
        toolbar_mode: 'wrap',

        contextmenu: 'link image imagetools table',
        skin: 'oxide',
        content_css: '/resources/theme/libs/fontawesome/css/all.min.css,/resources/theme/libs/tabler/dist/css/tabler.min.css,/resources/theme/libs/tabler/dist/css/tabler-flags.min.css,/resources/theme/libs/tabler/dist/css/tabler-payments.min.css,/resources/theme/libs/tabler/dist/css/tabler-buttons.min.css,/resources/theme/libs/tabler/dist/css/demo.min.css,/resources/theme/less/theme.less',
        content_style: options.css ? options.css : 'body {max-width: 1024px; padding: 32px !important;} ul {margin: 0;}'
    };
}