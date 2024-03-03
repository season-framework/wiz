String.prototype.number_format = function () {
    let num = parseFloat(this);
    if (isNaN(num)) return "0";
    return num.format();
};

String.prototype.string = function (len) {
    let s = '', i = 0;
    while (i++ < len) { s += this; }
    return s;
};

String.prototype.zf = function (len) {
    return "0".string(len - this.length) + this;
};