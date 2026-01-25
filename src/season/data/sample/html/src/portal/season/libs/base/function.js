Function.prototype.proceed = async (fn, obj) => {
    let args = fn.getParamNames();
    let params = [];
    for (let i = 0; i < args.length; i++) {
        let key = args[i];
        if (obj[key]) {
            params.push('obj["' + key + '"]');
        } else {
            params.push('null');
        }
    }

    let execstr = "let __wizformproc = async () => { await fn(" + params.join() + ")}; __wizformproc();";
    eval(execstr);
}

Function.prototype.getParamNames = function () {
    var STRIP_COMMENTS = /((\/\/.*$)|(\/\*[\s\S]*?\*\/))/mg;
    var ARGUMENT_NAMES = /([^\s,]+)/g;
    function getParamNames(func) {
        var fnStr = func.toString().replace(STRIP_COMMENTS, '');
        var result = fnStr.slice(fnStr.indexOf('(') + 1, fnStr.indexOf(')')).match(ARGUMENT_NAMES);
        if (result === null)
            result = [];
        return result;
    }
    return getParamNames(this);
}